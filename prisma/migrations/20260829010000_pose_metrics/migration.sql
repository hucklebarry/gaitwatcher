-- Preserve existing person-only job records while adding cascade timing and frame counters.
ALTER TABLE "ProcessingMetrics"
  ADD COLUMN "personDetectionMs" INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN "poseInferenceMs" INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN "bodyStateClassificationMs" INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN "framesSentToPersonDetector" INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN "framesSentToPoseModel" INTEGER NOT NULL DEFAULT 0;
