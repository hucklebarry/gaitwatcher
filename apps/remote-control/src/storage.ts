import {DeleteObjectCommand,GetObjectCommand,HeadObjectCommand,ListObjectsV2Command,PutObjectCommand,S3Client} from "@aws-sdk/client-s3";
import {getSignedUrl} from "@aws-sdk/s3-request-presigner";
import type {AudioAsset} from "@gaitwatcher/shared";

const required=(name:string)=>{const value=process.env[name];if(!value)throw new Error(`${name} is required`);return value};
export class AudioStorage{
 private bucket=required("AUDIO_STORAGE_BUCKET");private client=new S3Client({region:process.env.AUDIO_STORAGE_REGION??"auto",endpoint:required("AUDIO_STORAGE_ENDPOINT"),credentials:{accessKeyId:required("AUDIO_STORAGE_ACCESS_KEY_ID"),secretAccessKey:required("AUDIO_STORAGE_SECRET_ACCESS_KEY")}});
 private audioKey=(id:string)=>`audio-assets/${id}/source`;
 private metadataKey=(id:string)=>`audio-assets/${id}/metadata.json`;
 async uploadUrl(id:string,contentType:string){return getSignedUrl(this.client,new PutObjectCommand({Bucket:this.bucket,Key:this.audioKey(id),ContentType:contentType}),{expiresIn:300})}
 async finalize(asset:AudioAsset){const head=await this.client.send(new HeadObjectCommand({Bucket:this.bucket,Key:this.audioKey(asset.id)}));if(!head.ContentLength||head.ContentLength!==asset.sizeBytes||head.ContentType?.toLowerCase()!==asset.contentType.toLowerCase())throw new Error("uploaded audio did not match the requested metadata");await this.client.send(new PutObjectCommand({Bucket:this.bucket,Key:this.metadataKey(asset.id),Body:JSON.stringify(asset),ContentType:"application/json"}));return asset}
 async downloadUrl(asset:AudioAsset){return getSignedUrl(this.client,new GetObjectCommand({Bucket:this.bucket,Key:this.audioKey(asset.id)}),{expiresIn:300})}
 async list(){const listed=await this.client.send(new ListObjectsV2Command({Bucket:this.bucket,Prefix:"audio-assets/"}));const keys=(listed.Contents??[]).map(x=>x.Key).filter((key):key is string=>Boolean(key?.endsWith("/metadata.json")));const assets=await Promise.all(keys.map(async key=>{const object=await this.client.send(new GetObjectCommand({Bucket:this.bucket,Key:key}));return JSON.parse(await object.Body!.transformToString()) as AudioAsset}));return assets.filter(asset=>!asset.deletedAt).sort((a,b)=>b.createdAt.localeCompare(a.createdAt))}
 async delete(asset:AudioAsset){await Promise.all([this.client.send(new DeleteObjectCommand({Bucket:this.bucket,Key:this.audioKey(asset.id)})),this.client.send(new PutObjectCommand({Bucket:this.bucket,Key:this.metadataKey(asset.id),Body:JSON.stringify({...asset,deletedAt:new Date().toISOString()}),ContentType:"application/json"}))])}
}
