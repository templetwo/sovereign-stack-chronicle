-- chronicle_failure_profiles_v2 schema
--
-- Extracted verbatim from Gemini 3.5 Flash's chronicle_failure_profile v2
-- admission record, delivered via Anthony Vasquez Sr. as human relay during
-- cross-model design exchange, 2026-05-23.
--
-- Dialect: PostgreSQL (uses UUID, JSONB, TIMESTAMP WITH TIME ZONE,
-- gen_random_uuid()). Not directly portable to SQLite without adaptation.
--
-- Note: this DDL assumes a pre-existing `vector_admission_registry` table
-- that is altered by the first two statements. That parent table's full
-- schema is NOT provided in Gemini's v2 delivery. The ALTER statements
-- imply a table with at least a `vector_id` primary key column.
-- For verification work, create a minimal parent table first:
--
--   CREATE TABLE vector_admission_registry (
--       vector_id UUID PRIMARY KEY DEFAULT gen_random_uuid()
--   );
--
-- This is an underspecification in the v2 delivery worth flagging.
--
-- Companion files:
--   chronicle_failure_profile_v2.md (full admission record)
--   chronicle_failure_profile_loader.py (loading function, with known bugs preserved)
--   ARTIFACTS_README.md (provenance and intended use)

ALTER TABLE vector_admission_registry
DROP COLUMN IF EXISTS normalization_protocol,
DROP COLUMN IF EXISTS producer_node;

ALTER TABLE vector_admission_registry
ADD COLUMN normalization_rules_version VARCHAR(50) DEFAULT 'NFC_SpaceCollapse_LF_v1',
ADD COLUMN producer_source_node VARCHAR(50) CHECK (producer_source_node IN ('user-direct', 'system-proxy', 'replay-engine', 'human-relay'));

CREATE TABLE chronicle_failure_profiles_v2 (
    profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    registry_id UUID REFERENCES vector_admission_registry(vector_id) ON DELETE CASCADE,
    signature_hash CHAR(64) NOT NULL,
    temporal_window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    temporal_window_end TIMESTAMP WITH TIME ZONE NOT NULL,
    state_manifest JSONB NOT NULL, -- Format: [{"doc_id": "UUID", "sha256": "HEX_STRING"}]
    ocr_protocol_version VARCHAR(30) NOT NULL,
    is_active_audit_profile BOOLEAN DEFAULT TRUE NOT NULL
);
