import "dotenv/config";
import WebSocket from "ws";
import {ReolinkInteractiveDevice,isMessageId,type PlaybackStatus} from "../../../packages/interaction/src/index.js";

const cloudUrl=process.env.HOME_AGENT_CLOUD_URL;
const token=process.env.HOME_AGENT_TOKEN;
const agentId=process.env.HOME_AGENT_ID;
if(!cloudUrl||!token||!agentId)throw new Error("HOME_AGENT_CLOUD_URL, HOME_AGENT_TOKEN, and HOME_AGENT_ID are required");
const cloud=cloudUrl,agentToken=token,configuredAgentId=agentId;
const device=new ReolinkInteractiveDevice(),retryMs=Number(process.env.HOME_AGENT_RECONNECT_MS??5000);
let stopping=false;for(const signal of ["SIGINT","SIGTERM"] as const)process.on(signal,()=>{stopping=true});
const sleep=(ms:number)=>new Promise(resolve=>setTimeout(resolve,ms));
async function connect(){return new Promise<void>(resolve=>{const ws=new WebSocket(`${cloud.replace(/\/$/,"")}/agent?agentId=${encodeURIComponent(configuredAgentId)}`,{headers:{authorization:`Bearer ${agentToken}`}});const send=(payload:unknown)=>ws.readyState===WebSocket.OPEN&&ws.send(JSON.stringify(payload));ws.on("open",()=>{console.log(`Home Agent ${configuredAgentId} connected.`);send({type:"hello",agentId:configuredAgentId,deviceId:device.id})});ws.on("message",async raw=>{try{const command=JSON.parse(String(raw));if(command.type!=="play"||typeof command.commandId!=="string"||command.deviceId!==device.id||!isMessageId(command.messageId))return;const status=(state:PlaybackStatus,error?:string)=>send({type:"status",commandId:command.commandId,state,...(error?{error}:{})});status("agent_received");try{await device.playMessage(command.messageId,status);status("completed")}catch(error){status("failed",error instanceof Error?error.message.replace(/rtsp:\/\/\S+/g,"[redacted-rtsp]"):"playback failed")}}catch{}});ws.on("error",error=>console.error(`Home Agent connection error: ${error.message}`));ws.once("close",()=>resolve())})}
while(!stopping){await connect();if(!stopping){console.error(`Home Agent disconnected; retrying in ${retryMs} ms.`);await sleep(retryMs)}}
