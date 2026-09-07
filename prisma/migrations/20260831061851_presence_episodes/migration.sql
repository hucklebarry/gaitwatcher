-- AlterTable
ALTER TABLE "Observation" ADD COLUMN     "presenceEpisodeId" TEXT;

-- CreateTable
CREATE TABLE "PresenceEpisode" (
    "id" TEXT NOT NULL,
    "residentId" TEXT NOT NULL,
    "deviceId" TEXT NOT NULL,
    "room" TEXT,
    "startTime" TIMESTAMP(3) NOT NULL,
    "endTime" TIMESTAMP(3) NOT NULL,
    "confidence" DOUBLE PRECISION NOT NULL,
    "positiveSamples" INTEGER NOT NULL,
    "negativeSamples" INTEGER NOT NULL DEFAULT 0,
    "maxDetectionCount" INTEGER NOT NULL DEFAULT 1,
    "multiplePeopleSeen" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "PresenceEpisode_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "PresenceEpisode_residentId_startTime_idx" ON "PresenceEpisode"("residentId", "startTime");

-- CreateIndex
CREATE INDEX "PresenceEpisode_deviceId_endTime_idx" ON "PresenceEpisode"("deviceId", "endTime");

-- AddForeignKey
ALTER TABLE "Observation" ADD CONSTRAINT "Observation_presenceEpisodeId_fkey" FOREIGN KEY ("presenceEpisodeId") REFERENCES "PresenceEpisode"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "PresenceEpisode" ADD CONSTRAINT "PresenceEpisode_residentId_fkey" FOREIGN KEY ("residentId") REFERENCES "Resident"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "PresenceEpisode" ADD CONSTRAINT "PresenceEpisode_deviceId_fkey" FOREIGN KEY ("deviceId") REFERENCES "CameraDevice"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
