-- CreateEnum
CREATE TYPE "Provider" AS ENUM ('MOCK', 'RING');

-- CreateEnum
CREATE TYPE "EventStatus" AS ENUM ('QUEUED', 'PROCESSING', 'SUCCEEDED', 'FAILED', 'DEAD_LETTER');

-- CreateTable
CREATE TABLE "User" (
    "id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Household" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "consentedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Household_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Resident" (
    "id" TEXT NOT NULL,
    "householdId" TEXT NOT NULL,
    "name" TEXT NOT NULL,

    CONSTRAINT "Resident_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "CaregiverMembership" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "householdId" TEXT NOT NULL,
    "role" TEXT NOT NULL DEFAULT 'caregiver',

    CONSTRAINT "CaregiverMembership_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "CameraDevice" (
    "id" TEXT NOT NULL,
    "householdId" TEXT NOT NULL,
    "provider" "Provider" NOT NULL,
    "providerDeviceId" TEXT NOT NULL,
    "room" TEXT,
    "capabilities" JSONB NOT NULL,
    "linkStatus" TEXT NOT NULL DEFAULT 'linked',

    CONSTRAINT "CameraDevice_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "CameraEvent" (
    "id" TEXT NOT NULL,
    "idempotencyKey" TEXT NOT NULL,
    "deviceId" TEXT NOT NULL,
    "provider" "Provider" NOT NULL,
    "providerEventId" TEXT NOT NULL,
    "mediaId" TEXT NOT NULL,
    "occurredAt" TIMESTAMP(3) NOT NULL,
    "status" "EventStatus" NOT NULL DEFAULT 'QUEUED',
    "attempts" INTEGER NOT NULL DEFAULT 0,
    "error" TEXT,
    "queuedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "processedAt" TIMESTAMP(3),

    CONSTRAINT "CameraEvent_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Observation" (
    "id" TEXT NOT NULL,
    "residentId" TEXT NOT NULL,
    "deviceId" TEXT NOT NULL,
    "eventId" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "confidence" DOUBLE PRECISION NOT NULL,
    "timestamp" TIMESTAMP(3) NOT NULL,
    "metadata" JSONB NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Observation_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Alert" (
    "id" TEXT NOT NULL,
    "householdId" TEXT NOT NULL,
    "observationId" TEXT,
    "type" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'open',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Alert_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ProcessingMetrics" (
    "id" TEXT NOT NULL,
    "eventId" TEXT NOT NULL,
    "provider" "Provider" NOT NULL,
    "mediaBytesDownloaded" INTEGER NOT NULL,
    "framesDecoded" INTEGER NOT NULL,
    "framesAnalyzed" INTEGER NOT NULL,
    "cvProcessingMs" INTEGER NOT NULL,
    "totalJobMs" INTEGER NOT NULL,
    "temporaryBytesRetained" INTEGER NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ProcessingMetrics_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");

-- CreateIndex
CREATE UNIQUE INDEX "CaregiverMembership_userId_householdId_key" ON "CaregiverMembership"("userId", "householdId");

-- CreateIndex
CREATE UNIQUE INDEX "CameraDevice_provider_providerDeviceId_key" ON "CameraDevice"("provider", "providerDeviceId");

-- CreateIndex
CREATE UNIQUE INDEX "CameraEvent_idempotencyKey_key" ON "CameraEvent"("idempotencyKey");

-- CreateIndex
CREATE UNIQUE INDEX "Observation_eventId_key" ON "Observation"("eventId");

-- CreateIndex
CREATE UNIQUE INDEX "ProcessingMetrics_eventId_key" ON "ProcessingMetrics"("eventId");

-- AddForeignKey
ALTER TABLE "Resident" ADD CONSTRAINT "Resident_householdId_fkey" FOREIGN KEY ("householdId") REFERENCES "Household"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CaregiverMembership" ADD CONSTRAINT "CaregiverMembership_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CaregiverMembership" ADD CONSTRAINT "CaregiverMembership_householdId_fkey" FOREIGN KEY ("householdId") REFERENCES "Household"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CameraDevice" ADD CONSTRAINT "CameraDevice_householdId_fkey" FOREIGN KEY ("householdId") REFERENCES "Household"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CameraEvent" ADD CONSTRAINT "CameraEvent_deviceId_fkey" FOREIGN KEY ("deviceId") REFERENCES "CameraDevice"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Observation" ADD CONSTRAINT "Observation_residentId_fkey" FOREIGN KEY ("residentId") REFERENCES "Resident"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Observation" ADD CONSTRAINT "Observation_eventId_fkey" FOREIGN KEY ("eventId") REFERENCES "CameraEvent"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ProcessingMetrics" ADD CONSTRAINT "ProcessingMetrics_eventId_fkey" FOREIGN KEY ("eventId") REFERENCES "CameraEvent"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
