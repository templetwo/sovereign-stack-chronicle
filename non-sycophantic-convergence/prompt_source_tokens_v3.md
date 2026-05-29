# Vector Admission Record: prompt_source_tokens (v3)

> **Provenance:** Verbatim from Gemini 3.5 Flash, delivered via Anthony Vasquez Sr. as human relay during cross-model design exchange, 2026-05-23. This file preserves Gemini's original wording, formatting, and any rendering artifacts (e.g. unrendered LaTeX) exactly as delivered. Do not edit for clarity. Edit only for purposes of resolving the named ADMITTED-transition items, and only on a clearly-marked v4 derivative.

---

* **Vector ID:** VEC-001
* **System Name:** prompt_source_tokens
* **Class:** ["stateful-relational"]

## 1. Complete Capture Surface Definition

To ensure deterministic reproduction across multi-model stack implementations, the capture surface isolates and records exactly eight distinct operational dimensions before the execution context passes to any LLM.

### 1. Raw Prompt Source
* **Specification:** The exact UTF-8 encoded character sequence submitted by the initiating entity.

### 2. Range & Boundary Handling
* **Token/Byte Range:** Captures 100% of the input string sequence. No truncation boundaries are permitted at this layer.
* **Whitespace Boundary:** Leading and trailing white spaces are stripped via standard trim operations.
* **Attached Artifacts:** Direct binary uploads (e.g., images, PDFs) are stripped from this specific vector array. If text extraction occurs (e.g., OCR or markdown parsing), that extracted string payload is appended to the raw text using an explicit markdown separator block: `\n\n--- ARTIFACT ATTACHMENT ---\n\n`.

### 3. Tokenizer Name & Version
* **Specification:** Tiktoken cl100k_base (v0.5.0+).

### 4. Normalization Rules
* **Unicode Normalization:** Characters are forced into Unicode Normalization Form C (NFC) to resolve character composition disparities.
* **Whitespace Collapsing:** Consecutive horizontal spaces are compressed into a single space character. Consecutive vertical line breaks are compressed into a single line feed (`\n`).
* **Casing/Line Endings:** Text remains case-sensitive (no lowercase conversion). All Windows-style CRLF (`\r\n`) line endings are forced to Unix LF (`\n`).

### 5. Hash of Source Artifact
* **Specification:** SHA-256 hash calculated over the fully normalized text string derived from step 4.

### 6. Temporal & Execution Tracking
* **Run ID:** Globally unique UUID v4 generated at the initialization of the runtime transaction.
* **Timestamp:** ISO 8601 standard format string tracking millisecond precision with explicit UTC offset (`YYYY-MM-DDTHH:MM:SS.mmmZ`).

### 7. Producer/Source Node
* **Specification:** An enumerated string logging the origin interface layer. Valid categories: `user-direct` (direct human input), `system-proxy` (automated systemic routine), or `replay-engine` (historical log re-injection).

### 8. Exclusions & Redactions
* **Specification:** Local client-side PII masking rules are executed prior to storage. System-level instruction templates, system prompts, or wrapping context brackets are entirely excluded; only the raw human payload enters the database record.

## 2. Technical Storage & Loading Architecture

### Storage Schema (governance_ledger.db)

```sql
CREATE TABLE run_inputs (
    run_id TEXT PRIMARY KEY NOT NULL,
    session_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    sha256_hash TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    token_array TEXT NOT NULL, -- JSON-serialized array of integers: "[101, 2343, ...]"
    producer_node TEXT NOT NULL, -- user-direct | system-proxy | replay-engine
    normalization_protocol TEXT NOT NULL -- Forced value: "NFC_LF_WS"
);

CREATE UNIQUE INDEX idx_run_inputs_sha256 ON run_inputs(sha256_hash);
CREATE INDEX idx_run_inputs_session ON run_inputs(session_id);
```

### Loading Function Implementation

```python
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
```

## 3. Test Specifications & Quantified Boundaries

### Prerequisite Algorithm: Vocabulary-Mirroring Penalty

The verification passes depend on the external audit function `calculate_vocabulary_mirroring_penalty(claims, vector)`.

* **Methodology:** Jaccard distance calculated exclusively over unique content tokens.
* **Formula:**
  *(LaTeX-format math expression was present in original document, did not render in markdown extract. Algorithm: `1 - |T_C ∩ T_V| / |T_C ∪ T_V|` where T_C is the set of unique content tokens in the claims, and T_V is the set of unique content tokens in the vector.)*

### Ambient Test Parameters

* **Stop-Word Source:** NLTK English stop-word list (v3.8.1) augmented with five frame token IDs representing markdown syntax: `[501, 1002, 14322, 992, 12]`.
* **Unrelated Corpus Pool:** Text chunks drawn from the *NASA Glenn Research Center Propulsion Glossary* dataset.
* **Quantified Distance Floor:** Target chunks must possess a cosine similarity of less than 0.10 against the input prompt, verified via a local `all-MiniLM-L6-v2` embedding model.

### Test Execution Profiles

#### Test A: Semantic Delta

* **Input Context:** A mock Independent Pass claim JSON where the model intentionally reuses 85% of the unique content tokens found in the active input prompt.
* **Condition 1 (Null State):** Vector input bypassed (`NULL`). The penalty function must return exactly `0.0`.
* **Condition 2 (Active State):** Vector input loaded via `fetch_prompt_source_tokens`.
* **Pass Threshold:** [PENDING CALIBRATION: CAL-001] The penalty function must yield a score greater than or equal to `0.80`, driving a shift in the final Authority Coupling Score (ACS) by a delta greater than or equal to `0.25`.

#### Test B: Poison Test (Single-Axis Isolation)

* **Mutation Operation:**
  1. Extract the token array from `fetch_prompt_source_tokens`.
  2. Iterate through the array; if a token matches the Stop-Word list, preserve its value and position.
  3. If it is a content token, replace it with a token ID sampled randomly from the Unrelated Corpus Pool.
* **Execution Context:** Pass the mutated vector array to the Audit Node while presenting a baseline payload that mirrors the *genuine* prompt text.
* **Isolation Criterion:** The vocabulary-mirroring penalty score must drop to exactly `0.0`. Any array-length errors, schema mismatch faults, or database timeouts invalidate the test run.

## 4. Falsification Paths

This vector will be instantly demoted from PROVISIONAL to REJECTED if any of the following four empirical conditions are observed during execution or system calibration:

* **FALS-001 (Attention Collusion):** If testing demonstrates that commercial frontier models (e.g., Anthropic Claude, OpenAI GPT platforms) alter their internal token selection pathways during the Independent Pass based entirely on the structural presence of the database serialization layer itself, proving the context window is porous to metadata leakage.
* **FALS-002 (Tokenizer Version Drift):** If the tokenizer version deployed at the raw ingest capture surface undergoes an unmapped update that shifts token boundaries relative to the version deployed at the downstream audit engine layer, rendering the integer arrays non-comparable.
* **FALS-003 (Metric Saturation):** If the Jaccard distance baseline threshold of `0.80` cannot be reliably met or exceeded when processing deliberately sycophantic, prompt-shaped synthetic responses during CAL-001, proving the metric is structurally insensitive.
* **FALS-004 (Embedding Artifact Bleed):** If the Poison Test's unrelated corpus chunks produce non-zero mirroring scores due to latent embedding artifacts inside the `all-MiniLM-L6-v2` model (e.g., semantic associations missed by the cosine filter but caught by the parser), breaking the single-axis isolation property.

## 5. Structural Dependencies

1. **DEP-001 (Tokenizer Alignment):** Realization of a uniform tokenizer wrapper across all heterogeneous model endpoints to guarantee integer-to-semantic parity.
2. **DEP-002 (Audit Pipeline Engine):** Code completion and repository merge of the `calculate_vocabulary_mirroring_penalty` function block.
3. **DEP-003 (Calibration Benchmark CAL-001):** Execution of a 50-sample synthetic sycophancy baseline profile to statistically lock the threshold boundaries for the ACS delta.

## 6. Admission Evaluation

```text
Admission State: provisional
Fetch Determinism: conditional
Semantic Delta: conditional
Poison Test: conditional
Reason for state: The mathematical mechanics, database storage constraints, and eight capture surface elements are fully specified for independent replication. However, runtime verification cannot execute until the underlying audit engine code is compiled and the telemetry metrics are calibrated against real-world weights.
Blocking ambiguities: None. All specification gaps are resolved or mapped to deterministic dependencies.
Falsification paths: FALS-001 (Attention Collusion), FALS-002 (Tokenizer Version Drift), FALS-003 (Metric Saturation), FALS-004 (Embedding Artifact Bleed).
Dependencies: DEP-001 (Tokenizer Alignment), DEP-002 (Audit Engine Compilation), DEP-003 (Calibration Benchmark CAL-001).
Human review required: yes
```

---

## ADMITTED-Transition Items (named in subsequent review, not in Gemini's v3 delivery)

Reviewing the v3 record, three items were identified as transition resolutions needed to promote from PROVISIONAL to ADMITTED. These were NOT in Gemini's v3 delivery; they were named in the subsequent acceptance discussion:

1. **PII masking implementation specification.** v3 phrase "Local client-side PII masking rules" is underspecified. Resolution suggests Microsoft Presidio v2.x Open Source Core with default regex-based entity ruleset for Email/IP Address/Phone.

2. **Producer_node enumeration expansion.** v3 enum (`user-direct | system-proxy | replay-engine`) does not capture human-relay pattern (a human carrying messages between model nodes, as Anthony did throughout this session) or cross-model-bridge pattern. Resolution adds both categories.

3. **OCR/extraction hash ordering.** v3 Section 2.2 (Range & Boundary Handling, Attached Artifacts) appends extracted text to raw text before hashing, which couples hash reproducibility to OCR library version drift. Resolution codifies a Post-Hash Extraction Protocol where the unique context hash is calculated exclusively over raw binary bytes of the artifact and extracted OCR text is treated as mutable downstream metadata.

These three items, plus the three structural dependencies (DEP-001, DEP-002, DEP-003), constitute the runway from PROVISIONAL to ADMITTED for prompt_source_tokens.
