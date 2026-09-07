import {describe,expect,it} from "vitest";
import {isMessageId,messageCatalog} from "../packages/interaction/src/index.js";
describe("interaction message catalog",()=>{it("accepts only committed message IDs",()=>{expect(Object.keys(messageCatalog)).toEqual(["audio_test","lunch_reminder","walk_reminder","family_checkin"]);expect(isMessageId("lunch_reminder")).toBe(true);expect(isMessageId("../secret.wav")).toBe(false);expect(isMessageId("anything")).toBe(false)})});
