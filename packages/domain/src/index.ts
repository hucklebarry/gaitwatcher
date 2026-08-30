export type DeviceCapabilities = { video:boolean; inboundAudio:boolean; outboundAudio:boolean; fullDuplexTalk:boolean; ptz:boolean; continuousStreaming:boolean; eventClips:boolean };
export type CameraDevice = { id:string; provider:"mock"|"ring"; providerDeviceId:string; room?:string; capabilities:DeviceCapabilities };
export type MediaReference = { providerMediaId:string; localPath?:string; url?:string };
export interface CameraProvider { listDevices():Promise<CameraDevice[]>; subscribeToEvents():Promise<void>; getEventMedia(eventId:string):Promise<MediaReference>; getSnapshot?():Promise<MediaReference>; getLiveStream?():Promise<{url:string}> }
export type BodyState="standing"|"sitting"|"floor_level"|"unknown";
export type CvResult={personDetected:boolean;personConfidence:number;poseDetected:boolean;poseConfidence:number;bodyState:BodyState;bodyStateConfidence:number;framesDecoded:number;framesAnalyzed:number;framesSentToPersonDetector:number;framesSentToPoseModel:number;personDetectionMs:number;poseInferenceMs:number;bodyStateClassificationMs:number;totalProcessingMs:number;landmarks?:Record<string,unknown>};
