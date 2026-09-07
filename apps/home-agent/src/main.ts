import {config as loadEnv} from "dotenv";
import {fileURLToPath} from "node:url";
import {dirname,resolve} from "node:path";
import {mkdtemp,rm,writeFile} from "node:fs/promises";
import {tmpdir} from "node:os";
import WebSocket from "ws";
import {ReolinkInteractiveDevice} from "@gaitwatcher/interaction";
import {isMessageId,type InteractionStatus} from "@gaitwatcher/shared";

loadEnv({path:process.env.HOME_AGENT_ENV_FILE??resolve(dirname(fileURLToPath(import.meta.url)),"../../..",".env")});

const cloudUrl=process.env.HOME_AGENT_CLOUD_URL;
const agentId=process.env.HOME_AGENT_ID;
if(!cloudUrl||!agentId)throw new Error("HOME_AGENT_CLOUD_URL and HOME_AGENT_ID are required");
const cloud=cloudUrl,configuredAgentId=agentId;
const device=new ReolinkInteractiveDevice(),retryMs=Number(process.env.HOME_AGENT_RECONNECT_MS??5000);
let stopping=false;for(const signal of ["SIGINT","SIGTERM"] as const)process.on(signal,()=>{stopping=true});
const sleep=(ms:number)=>new Promise(resolve=>setTimeout(resolve,ms));
async function playAsset(downloadUrl:string,onStatus:(status:InteractionStatus)=>void){const response=await fetch(downloadUrl);if(!response.ok)throw new Error(`asset download failed (${response.status})`);const directory=await mkdtemp(resolve(tmpdir(),"gaitwatcher-audio-asset-"));const file=resolve(directory,"recording");try{await writeFile(file,Buffer.from(await response.arrayBuffer()));await device.playAudioFile(file,onStatus)}finally{await rm(directory,{recursive:true,force:true})}}
async function connect(){return new Promise<void>(resolve=>{const ws=new WebSocket(`${cloud.replace(/\/$/,"")}/agent?agentId=${encodeURIComponent(configuredAgentId)}`);const send=(payload:unknown)=>ws.readyState===WebSocket.OPEN&&ws.send(JSON.stringify(payload));ws.on("open",()=>{console.log(`Home Agent ${configuredAgentId} connected.`);send({type:"hello",agentId:configuredAgentId,deviceId:device.id})});ws.on("message",async raw=>{try{const command=JSON.parse(String(raw));if(typeof command.commandId!=="string"||command.deviceId!==device.id)return;const status=(state:InteractionStatus,error?:string)=>send({type:"status",commandId:command.commandId,state,...(error?{error}:{})});status("agent_received");try{if(command.type==="play"&&isMessageId(command.messageId))await device.playMessage(command.messageId,status);else if(command.type==="play_asset"&&typeof command.downloadUrl==="string")await playAsset(command.downloadUrl,status);else return;status("completed")}catch(error){status("failed",error instanceof Error?error.message.replace(/https?:\/\/\S+|rtsp:\/\/\S+/g,"[redacted-url]"):"playback failed")}}catch{}});ws.on("error",error=>console.error(`Home Agent connection error: ${error.message}`));ws.once("close",()=>resolve())})}
while(!stopping){await connect();if(!stopping){console.error(`Home Agent disconnected; retrying in ${retryMs} ms.`);await sleep(retryMs)}}
