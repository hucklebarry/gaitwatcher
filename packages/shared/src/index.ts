export const messageCatalog={audio_test:{label:"Audio Test"},lunch_reminder:{label:"Lunch Reminder"},walk_reminder:{label:"Walk Reminder"},family_checkin:{label:"Family Check-in"}} as const;
export type MessageId=keyof typeof messageCatalog;
export type InteractionStatus="requested"|"agent_received"|"camera_playback_started"|"completed"|"failed";
export function isMessageId(value:unknown):value is MessageId{return typeof value==="string"&&value in messageCatalog}
