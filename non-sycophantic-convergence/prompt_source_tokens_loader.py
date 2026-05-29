"""
fetch_prompt_source_tokens
==========================

Extracted verbatim from Gemini 3.5 Flash's prompt_source_tokens v3 admission record,
delivered via Anthony Vasquez Sr. as human relay during cross-model design exchange,
2026-05-23.

Provenance: cross-model transcript -> conversation document upload -> this file.

This file is for Tier 2 verification work in the non-sycophantic-convergence
build phase. Do not edit before verification confirms the function behaves as
the chronicle entry describes.

Companion files:
- prompt_source_tokens_v3.md (full admission record)
- prompt_source_tokens_ddl.sql (governance_ledger.db schema)
- ARTIFACTS_README.md (provenance and intended use)
"""

import json
import sqlite3


def fetch_prompt_source_tokens(db_path: str, run_id: str) -> list[int]:
    """
    Retrieves the raw token ID array for a specific run from the ledger.
    Guarantees deterministic array return or raises explicit KeyError.
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT token_array FROM run_inputs WHERE run_id = ?",
            (run_id,)
        )
        row = cursor.fetchone()

    if row is None:
        raise KeyError(f"Run ID {run_id} not found in governance ledger.")

    return json.loads(row[0])
