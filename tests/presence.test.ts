import {describe,it,expect} from "vitest";import {aggregatePresence,dailyPresence} from "../packages/domain/src/presence.js";
const t=(minute:number,evidence:any="present")=>({at:new Date(minute*60_000),evidence,confidence:.9,detectionCount:1});
describe("presence aggregation",()=>{
 it("merges a brief detector miss",()=>expect(aggregatePresence([t(0),t(1),t(2,"no_person"),t(3)]).length).toBe(1));
 it("suppresses a one-sample blip",()=>expect(aggregatePresence([t(0)]).length).toBe(0));
 it("splits separate visits",()=>expect(aggregatePresence([t(0),t(1),t(8),t(9)]).length).toBe(2));
 it("retains multiple-person metadata",()=>expect(aggregatePresence([{...t(0),detectionCount:2},t(1)])[0].multiplePeopleSeen).toBe(true));
 it("derives daily totals",()=>expect(dailyPresence([{...aggregatePresence([t(0),t(1)])[0],room:"kitchen"}]).presenceMsByRoom.kitchen).toBe(60_000));
});
