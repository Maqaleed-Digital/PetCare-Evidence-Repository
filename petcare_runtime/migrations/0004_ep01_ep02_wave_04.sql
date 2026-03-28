-- Migration: 0004_ep01_ep02_wave_04
-- Wave 04: consent-document linkage columns, document upload policy index
-- No structural schema change required; consent linkage is enforced at service layer.
-- This migration is a governed checkpoint only.

-- Checkpoint: wave 04 runtime additions are service-layer and route-layer only.
-- Protected-zone semantics unchanged.
SELECT 1; -- checkpoint
