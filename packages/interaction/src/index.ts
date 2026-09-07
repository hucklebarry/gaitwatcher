import {dirname,resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {getStreamUris,playFile} from "rtsp-backchannel";
import {messageCatalog,type InteractionStatus,type MessageId} from "@gaitwatcher/shared";

const messageFiles:Record<MessageId,string>={audio_test:"fixtures/audio/audio-test.mp3",lunch_reminder:"fixtures/audio/lunch-reminder.mp3",walk_reminder:"fixtures/audio/walk-reminder.mp3",family_checkin:"fixtures/audio/family-checkin.mp3"};
export type InteractiveDevice={id:string;playMessage(messageId:MessageId,onStatus:(status:InteractionStatus)=>void):Promise<void>};
const env=(...names:string[])=>{for(const name of names){const value=process.env[name]?.trim();if(value)return value}throw new Error(`${names.join(" or ")} is required`)};

export class ReolinkInteractiveDevice implements InteractiveDevice{
 readonly id:string; private host:string;private user:string;private pass:string;private onvifPort:number;
 constructor(){this.id=env("HOME_AGENT_DEVICE_ID","REOLINK_DEVICE_ID");this.host=env("REOLINK_HOST","REOLINK_LIVING_ROOM_CAMERA_IP");this.user=env("REOLINK_USERNAME","REOLINK_LIVING_ROOM_USERNAME");this.pass=env("REOLINK_PASSWORD","REOLINK_LIVING_ROOM_CAMERA_PASSWORD");this.onvifPort=Number(process.env.REOLINK_ONVIF_PORT??8000)}
 async playMessage(messageId:MessageId,onStatus:(status:InteractionStatus)=>void){
  const fixture=resolve(dirname(fileURLToPath(import.meta.url)),"../../..",messageFiles[messageId]);
  await this.playAudioFile(fixture,onStatus);
 }
 async playAudioFile(file:string,onStatus:(status:InteractionStatus)=>void){
  const deviceUrls=[`http://${this.host}:${this.onvifPort}/onvif/device_service`];
  const stream=(await getStreamUris({host:this.host,user:this.user,pass:this.pass,deviceUrls,timeoutMs:Number(process.env.REOLINK_TIMEOUT_MS??8000)}))[0];
  if(!stream)throw new Error("camera did not return an RTSP stream URI");
  onStatus("camera_playback_started");
  await playFile({host:stream.uri,user:this.user,pass:this.pass,file,volume:Number(process.env.REOLINK_AUDIO_VOLUME??0.05),codec:"auto"});
 }
}
