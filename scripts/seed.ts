import {PrismaClient,Provider} from "@prisma/client";
const db=new PrismaClient();
const household=await db.household.upsert({where:{id:"demo-household"},update:{},create:{id:"demo-household",name:"Demo household",consentedAt:new Date()}});
const user=await db.user.upsert({where:{email:"caregiver@example.test"},update:{},create:{email:"caregiver@example.test"}});
await db.resident.upsert({where:{id:"demo-resident"},update:{},create:{id:"demo-resident",name:"Margaret",householdId:household.id}});
await db.caregiverMembership.upsert({where:{userId_householdId:{userId:user.id,householdId:household.id}},update:{},create:{userId:user.id,householdId:household.id}});
await db.cameraDevice.upsert({where:{id:"mock-front"},update:{},create:{id:"mock-front",householdId:household.id,provider:Provider.MOCK,providerDeviceId:"front-door",room:"entryway",capabilities:{video:true,inboundAudio:false,outboundAudio:false,fullDuplexTalk:false,ptz:false,continuousStreaming:false,eventClips:true}}});
console.log(JSON.stringify({householdId:household.id,userId:user.id,deviceId:"mock-front"})); await db.$disconnect();
