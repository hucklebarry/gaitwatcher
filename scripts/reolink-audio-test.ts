import "dotenv/config";
import {spawnSync} from "node:child_process";
import {mkdtemp,rm} from "node:fs/promises";
import {tmpdir} from "node:os";
import {join,resolve} from "node:path";
import {getCameraCapabilities,getStreamUris,playFile,type CodecPreference} from "rtsp-backchannel";

type Settings={host:string;username:string;password:string;audioFile?:string;volume:number;codec:CodecPreference;onvifPort:number;timeoutMs:number;verbose:boolean};

const codecs=new Set<CodecPreference>(["auto","pcma","pcmu","g726-16","g726-24","g726-32","g726-40","aac"]);

function required(...names:string[]){for(const name of names){const value=process.env[name]?.trim();if(value)return value}throw new Error(`${names.join(" or ")} is required`)}
function numberSetting(name:string,fallback:number,{min,max}:{min:number;max:number}){const raw=process.env[name];if(raw===undefined||raw==="")return fallback;const value=Number(raw);if(!Number.isFinite(value)||value<min||value>max)throw new Error(`${name} must be between ${min} and ${max}`);return value}
function settings():Settings{
 const codec=(process.env.REOLINK_AUDIO_CODEC??"auto").toLowerCase() as CodecPreference;
 if(!codecs.has(codec))throw new Error(`REOLINK_AUDIO_CODEC must be one of: ${[...codecs].join(", ")}`);
 return {host:required("REOLINK_HOST","REOLINK_LIVING_ROOM_CAMERA_IP"),username:required("REOLINK_USERNAME","REOLINK_LIVING_ROOM_USERNAME"),password:required("REOLINK_PASSWORD","REOLINK_LIVING_ROOM_CAMERA_PASSWORD"),audioFile:process.env.REOLINK_AUDIO_FILE?resolve(process.env.REOLINK_AUDIO_FILE):undefined,volume:numberSetting("REOLINK_AUDIO_VOLUME",0.05,{min:0,max:1}),codec,onvifPort:numberSetting("REOLINK_ONVIF_PORT",8000,{min:1,max:65535}),timeoutMs:numberSetting("REOLINK_TIMEOUT_MS",8000,{min:1,max:86_400_000}),verbose:process.env.REOLINK_AUDIO_VERBOSE==="1"};
}
function runFfmpeg(args:string[],stage:string){const result=spawnSync("ffmpeg",args,{encoding:"utf8"});if(result.error)throw new Error(`${stage}: ffmpeg is unavailable (${result.error.message})`);if(result.status!==0)throw new Error(`${stage}: ffmpeg exited ${result.status}${result.stderr?`: ${result.stderr.trim()}`:""}`)}
function requireFfmpeg(){runFfmpeg(["-version"],"Checking audio tooling")}
async function temporaryTone(){const directory=await mkdtemp(join(tmpdir(),"gaitwatcher-reolink-audio-"));const file=join(directory,"audio-test-tone.wav");runFfmpeg(["-nostdin","-hide_banner","-loglevel","error","-f","lavfi","-i","sine=frequency=880:sample_rate=48000","-t","1","-ac","1","-c:a","pcm_s16le",file],"Creating default test tone");return {directory,file}}
function safeError(error:unknown,password:string){let message=error instanceof Error?error.message:String(error);if(password)message=message.replaceAll(password,"[redacted]");return message.replace(/rtsp:\/\/[^\s@/]+(?::[^\s@/]*)?@/gi,"rtsp://[redacted]@");}
function failureKind(message:string){const lower=message.toLowerCase();if(lower.includes(" is required")||lower.includes("must be between")||lower.includes("must be one of"))return "configuration failure";if(lower.includes("ffmpeg"))return "audio conversion/tooling failure";if(lower.includes("authentication")||lower.includes("unauthorized")||lower.includes("401"))return "authentication failure";if(lower.includes("sendonly")||lower.includes("backchannel audio track")||lower.includes("supported backchannel audio codec"))return "unsupported ONVIF/RTSP backchannel capability";if(lower.includes("options ")||lower.includes("describe")||lower.includes("setup")||lower.includes("play ")||lower.includes("rtsp"))return "RTSP/backchannel negotiation or session failure";if(lower.includes("connect")||lower.includes("request failed")||lower.includes("econn")||lower.includes("enotfound")||lower.includes("timeout"))return "network or ONVIF connection failure";return "library/protocol limitation or unexpected failure"}
function logCapabilitySummary(report:Awaited<ReturnType<typeof getCameraCapabilities>>,verbose:boolean){
 const audioProfiles=report.profiles.filter(profile=>profile.hasAudioOutput);
 console.log(`Authenticated. Device reports ${report.profiles.length} media profile(s); ${audioProfiles.length} include AudioOutputConfiguration.`);
 console.log(`Declared ONVIF profiles: ${report.declaredProfiles.join(", ")||"none reported"}. Media2: ${report.media2.detected===true?"advertised":report.media2.detected===false?"not advertised":"unknown"}.`);
 if(audioProfiles.length)console.log(`Audio-output profile token(s): ${audioProfiles.map(profile=>profile.token).join(", ")}.`);
 else console.log("No ONVIF AudioOutputConfiguration was reported. Playback will still perform the definitive RTSP sendonly-backchannel check.");
 if(report.warnings.length)console.log(`Capability discovery completed with ${report.warnings.length} non-fatal warning(s). Set REOLINK_AUDIO_VERBOSE=1 for details.`);
 if(verbose)console.log(JSON.stringify({device:report.device,declaredProfiles:report.declaredProfiles,services:report.services,profiles:report.profiles,media2:report.media2,warnings:report.warnings},null,2));
}

let config:Settings|undefined;
let temporary:{directory:string;file:string}|undefined;
const started=performance.now();
try {
 config=settings();
 requireFfmpeg();
 console.log("Connecting to camera for ONVIF capability discovery...");
 const deviceUrls=[`http://${config.host}:${config.onvifPort}/onvif/device_service`];
 const report=await getCameraCapabilities({host:config.host,user:config.username,pass:config.password,deviceUrls,timeoutMs:config.timeoutMs});
 logCapabilitySummary(report,config.verbose);
 const streams=await getStreamUris({host:config.host,user:config.username,pass:config.password,deviceUrls,timeoutMs:config.timeoutMs});
 const stream=streams[0];
 if(!stream)throw new Error("ONVIF did not return a media-profile RTSP URI");
 console.log(`Resolved RTSP URI for ONVIF profile ${stream.profileToken}; credentials remain out of the URI and logs.`);
 if(!config.audioFile){temporary=await temporaryTone();console.log("No REOLINK_AUDIO_FILE supplied; using a generated 880 Hz, one-second WAV tone.");}
 console.log("Opening outbound audio session and negotiating an RTSP backchannel...");
 const packets=await playFile({host:stream.uri,user:config.username,pass:config.password,file:config.audioFile??temporary!.file,volume:config.volume,codec:config.codec});
 console.log(`Finished: sent ${packets} RTP packet(s) in ${Math.round(performance.now()-started)} ms.`);
 console.log("Manual result required: confirm whether the camera speaker emitted the audio. A successful session proves standards-based backchannel negotiation; it does not by itself prove audibility.");
} catch(error) {
 const message=safeError(error,config?.password??"");
 console.error(`Audio spike failed (${failureKind(message)}): ${message}`);
 process.exitCode=1;
} finally {if(temporary)await rm(temporary.directory,{recursive:true,force:true});}
