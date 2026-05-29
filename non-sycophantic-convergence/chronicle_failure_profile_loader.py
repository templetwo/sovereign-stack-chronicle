"""
deterministic_load_chronicle_state
==================================

Extracted verbatim from Gemini 3.5 Flash's chronicle_failure_profile v2 admission
record, delivered via Anthony Vasquez Sr. as human relay during cross-model
design exchange, 2026-05-23.

Provenance: cross-model transcript -> conversation document upload -> this file.

================================================================================
KNOWN ISSUES PRESERVED AS-DELIVERED FOR TIER 2 VERIFICATION
================================================================================

This file contains three bugs identified during the design exchange but
deliberately left intact. DO NOT FIX before Tier 2 verification work
confirms the bugs reproduce when the file is run as-is.

Bug 1: Missing import.
  `unicodedata` is referenced inside the function but not imported.
  Adding the import is the obvious fix; the question is whether Gemini
  intended the import implicit/global or actually missed it.

Bug 2: Noop encode/decode roundtrip.
  Inside the loop:
      normalized_text = normalized_text.encode("utf-8")
      normalized_text = unicodedata.normalize("NFC", normalized_text.decode("utf-8"))
  The encode then decode accomplishes nothing. unicodedata.normalize accepts
  str and returns str; passing it the decoded form of the encoded form is
  identical to passing the original str. The roundtrip should be removed.

Bug 3: NFC normalization order.
  Current pipeline order:
      strip -> split/join (whitespace collapse) -> replace CRLF -> encode/decode -> NFC
  Canonically NFC should happen FIRST, since NFC can produce character-width
  changes that affect whitespace handling downstream. The correct order is:
      NFC -> strip -> split/join (whitespace collapse) -> replace CRLF
  The hash is computed over the final normalized form, so this ordering bug
  affects reproducibility across implementations that normalize differently.

These bugs are the test material. If the file with the bugs intact reproduces
the bugs when run, the exchange's identification of them is verified. If
running reveals additional bugs not previously identified, that is new signal
worth chronicling under the format-divergence methodology finding.

================================================================================

Companion files:
- chronicle_failure_profile_v2.md (full admission record)
- chronicle_failure_profile_ddl.sql (PostgreSQL schema)
- ARTIFACTS_README.md (provenance and intended use)

Note on database: the function signature accepts sqlite3.Connection, but the
DDL uses PostgreSQL-specific features (UUID, JSONB, TIMESTAMP WITH TIME ZONE,
gen_random_uuid()). For local verification, either adapt the DDL to SQLite
or adapt the function signature to psycopg2/asyncpg. As-delivered, the file
contains this mismatch unaddressed.
"""

import json
import hashlib
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Tuple


class StateLoadingEngineError(Exception): """Base exception for deterministic loader failures."""

class ManifestHashMismatchError(StateLoadingEngineError): """Raised when a document hash deviates from the manifest."""

class BoundaryBreachError(StateLoadingEngineError): """Raised when a document violates temporal limits."""


def deterministic_load_chronicle_state(
    db_conn: sqlite3.Connection,
    profile_id: str
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Reconstitutes the exact multi-document token stream from archived state manifests,
    enforcing explicit temporal and cryptographic isolation properties.
    """
    cursor = db_conn.cursor()

    # 1. Retrieve the frozen execution profile parameters
    cursor.execute(
        """SELECT temporal_window_start, temporal_window_end, state_manifest
           FROM chronicle_failure_profiles_v2 WHERE profile_id = ?""",
        (profile_id,)
    )
    row = cursor.fetchone()
    if not row:
        raise StateLoadingEngineError(f"Profile {profile_id} not found in registry.")

    t_start_str, t_end_str, manifest_json = row
    t_start = datetime.fromisoformat(t_start_str)
    t_end = datetime.fromisoformat(t_end_str)
    manifest = json.loads(manifest_json) # Expected structure: [{"doc_id": "...", "sha256": "..."}]

    reconstituted_normalized_payloads = []

    # 2. Iterate through manifest to verify point-in-time state
    for entry in sorted(manifest, key=lambda x: x["doc_id"]):
        doc_id = entry["doc_id"]
        expected_sha = entry["sha256"]

        cursor.execute(
            """SELECT raw_text, log_timestamp FROM chronicle_ledger
               WHERE doc_id = ?""", (doc_id,)
        )
        log_row = cursor.fetchone()
        if not log_row:
            raise StateLoadingEngineError(f"Critical Log Record {doc_id} missing from ledger.")

        raw_text, log_time_str = log_row
        log_time = datetime.fromisoformat(log_time_str)

        # Enforce temporal window boundaries
        if not (t_start <= log_time <= t_end):
            raise BoundaryBreachError(f"Record {doc_id} timestamp {log_time_str} out of bounds.")

        # Execute capture-surface canonical normalization rules
        normalized_text = raw_text.strip()
        normalized_text = " ".join(normalized_text.split()) # Collapse inline whitespace
        normalized_text = normalized_text.replace("\r\n", "\n") # Line-ending uniformity
        normalized_text = normalized_text.encode("utf-8")
        normalized_text = unicodedata.normalize("NFC", normalized_text.decode("utf-8"))

        # Validate cryptographic integrity against frozen manifest
        current_sha = hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()
        if current_sha != expected_sha:
            raise ManifestHashMismatchError(f"Hash deviation detected on record {doc_id}.")

        reconstituted_normalized_payloads.append(normalized_text)

    # 3. Formulate unique, reproducible signature input hash string
    final_concatenated_stream = "".join(reconstituted_normalized_payloads)
    calculated_signature_hash = hashlib.sha256(final_concatenated_stream.encode("utf-8")).hexdigest()

    return calculated_signature_hash, manifest
