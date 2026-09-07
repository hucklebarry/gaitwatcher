import "dotenv/config";
import {spawn} from "node:child_process";
import {copyFile,mkdir,writeFile} from "node:fs/promises";
import {join,resolve} from "node:path";
import {getStreamUris,playFile} from "rtsp-backchannel";

type Config={host:string;user:string;pass:string;onvifPort:number;timeoutMs:number;file:string;captureSeconds:number;sessions:number;gapSeconds:number;outputDir:string};
function required(...names:string[]){for(const name of names){const value=process.env[name]?.trim();if(value)return value}throw new Error(`${names.join(" or ")} is required`)}
function numberValue(name:string,fallback:number,min:number,max:number){const value=Number(process.env[name]??fallback);if(!Number.isFinite(value)||value<min||value>max)throw new Error(`${name} must be between ${min} and ${max}`);return value}
function config():Config{return {host:required("REOLINK_HOST","REOLINK_LIVING_ROOM_CAMERA_IP"),user:required("REOLINK_USERNAME","REOLINK_LIVING_ROOM_USERNAME"),pass:required("REOLINK_PASSWORD","REOLINK_LIVING_ROOM_CAMERA_PASSWORD"),onvifPort:numberValue("REOLINK_ONVIF_PORT",8000,1,65535),timeoutMs:numberValue("REOLINK_TIMEOUT_MS",8000,1,86_400_000),file:resolve(required("REOLINK_AUDIO_FILE")),captureSeconds:numberValue("REOLINK_CAPTURE_SECONDS",10,1,120),sessions:numberValue("REOLINK_DUPLEX_SESSIONS",3,1,10),gapSeconds:numberValue("REOLINK_DUPLEX_GAP_SECONDS",2,0,30),outputDir:resolve(process.env.REOLINK_CAPTURE_DIR??join("data","local","reolink-audio",new Date().toISOString().replace(/[:.]/g,"-")))}}
const sleep=(ms:number)=>new Promise(resolve=>setTimeout(resolve,ms));
function safe(message:string,pass:string){return message.replaceAll(pass,"[redacted]").replace(/rtsp:\/\/[^\s@/]+(?::[^\s@/]*)?@/gi,"rtsp://[redacted]@")}
function capture(streamUri:string,c:Config,file:string){const url=new URL(streamUri);url.username=c.user;url.password=c.pass;const args=["-nostdin","-hide_banner","-loglevel","error","-rtsp_transport","tcp","-i",url.toString(),"-map","0:a:0","-vn","-t",String(c.captureSeconds),"-ac","1","-c:a","pcm_s16le",file];const child=spawn("ffmpeg",args,{stdio:["ignore","ignore","pipe"]});let stderr="";child.stderr.on("data",chunk=>stderr+=chunk);return new Promise<void>((resolve,reject)=>{child.once("error",error=>reject(error));child.once("close",code=>code===0?resolve():reject(new Error(`ffmpeg inbound capture exited ${code}: ${stderr.trim()}`)))})}

const c=config();
await mkdir(c.outputDir,{recursive:true});
await copyFile(c.file,join(c.outputDir,"outbound-speech.wav"));
const deviceUrls=[`http://${c.host}:${c.onvifPort}/onvif/device_service`];
console.log("Resolving the camera RTSP microphone stream through ONVIF...");
const stream=(await getStreamUris({host:c.host,user:c.user,pass:c.pass,deviceUrls,timeoutMs:c.timeoutMs}))[0];
if(!stream)throw new Error("ONVIF did not return an RTSP stream URI");
const report:{startedAt:string;captureSeconds:number;sessions:{index:number;captureFile:string;outboundPackets?:number;outboundSessionMs?:number;elapsedMs:number;error?:string}[]}={startedAt:new Date().toISOString(),captureSeconds:c.captureSeconds,sessions:[]};
for(let index=1;index<=c.sessions;index++){
 const captureFile=join(c.outputDir,`session-${index}-microphone.wav`),started=performance.now();
 const row={index,captureFile,elapsedMs:0} as typeof report.sessions[number];report.sessions.push(row);
 try{
  console.log(`Session ${index}/${c.sessions}: capturing microphone audio for ${c.captureSeconds}s...`);
  const inbound=capture(stream.uri,c,captureFile);
  await sleep(1000);
  console.log(`Session ${index}/${c.sessions}: sending speech while capture remains open...`);
  const outboundStarted=performance.now();
  row.outboundPackets=await playFile({host:stream.uri,user:c.user,pass:c.pass,file:c.file,volume:Number(process.env.REOLINK_AUDIO_VOLUME??0.05),codec:"auto"});
  row.outboundSessionMs=Math.round(performance.now()-outboundStarted);
  await inbound;
  console.log(`Session ${index}/${c.sessions}: capture written to ${captureFile}`);
 }catch(error){row.error=safe(error instanceof Error?error.message:String(error),c.pass);console.error(`Session ${index}/${c.sessions} failed: ${row.error}`)}
 finally{row.elapsedMs=Math.round(performance.now()-started)}
 if(index<c.sessions)await sleep(c.gapSeconds*1000);
}
await writeFile(join(c.outputDir,"report.json"),JSON.stringify(report,null,2)+"\n");
const failures=report.sessions.filter(session=>session.error).length;
console.log(`Finished ${c.sessions} session(s): ${failures} failure(s). Review outbound-speech.wav, each microphone WAV, and report.json in: ${c.outputDir}`);
console.log("Manual review required: play each WAV while noting whether room speech remains intelligible during speaker playback. Classify duplex behavior as full duplex, half duplex, push-to-talk-like, or unclear; this script does not infer it from packet success alone.");
if(failures)process.exitCode=1;
