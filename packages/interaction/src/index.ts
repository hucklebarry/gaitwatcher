import {resolve} from "node:path";
import {getStreamUris,playFile} from "rtsp-backchannel";

export const messageCatalog={
 audio_test:{label:"Audio Test",file:"fixtures/audio/audio-test.wav"},
 lunch_reminder:{label:"Lunch Reminder",file:"fixtures/audio/lunch-reminder.wav"},
 walk_reminder:{label:"Walk Reminder",file:"fixtures/audio/walk-reminder.wav"},
 family_checkin:{label:"Family Check-in",file:"fixtures/audio/family-checkin.wav"},
} as const;
export type MessageId=keyof typeof messageCatalog;
export type PlaybackStatus="agent_received"|"camera_playback_started"|"completed"|"failed";
export function isMessageId(value:unknown):value is MessageId{return typeof value==="string"&&value in messageCatalog}
export type InteractiveDevice={id:string;playMessage(messageId:MessageId,onStatus:(status:PlaybackStatus)=>void):Promise<void>};
const env=(...names:string[])=>{for(const name of names){const value=process.env[name]?.trim();if(value)return value}throw new Error(`${names.join(" or ")} is required`)};

export class ReolinkInteractiveDevice implements InteractiveDevice{
 readonly id:string; private host:string;private user:string;private pass:string;private onvifPort:number;
 constructor(){this.id=env("HOME_AGENT_DEVICE_ID","REOLINK_DEVICE_ID");this.host=env("REOLINK_HOST","REOLINK_LIVING_ROOM_CAMERA_IP");this.user=env("REOLINK_USERNAME","REOLINK_LIVING_ROOM_USERNAME");this.pass=env("REOLINK_PASSWORD","REOLINK_LIVING_ROOM_CAMERA_PASSWORD");this.onvifPort=Number(process.env.REOLINK_ONVIF_PORT??8000)}
 async playMessage(messageId:MessageId,onStatus:(status:PlaybackStatus)=>void){
  const message=messageCatalog[messageId], deviceUrls=[`http://${this.host}:${this.onvifPort}/onvif/device_service`];
  const stream=(await getStreamUris({host:this.host,user:this.user,pass:this.pass,deviceUrls,timeoutMs:Number(process.env.REOLINK_TIMEOUT_MS??8000)}))[0];
  if(!stream)throw new Error("camera did not return an RTSP stream URI");
  onStatus("camera_playback_started");
  await playFile({host:stream.uri,user:this.user,pass:this.pass,file:resolve(message.file),volume:Number(process.env.REOLINK_AUDIO_VOLUME??0.05),codec:"auto"});
 }
}
