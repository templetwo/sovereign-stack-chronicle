"""
Tier 2 verification harness for chronicle_failure_profile_loader.py

Tests the VERBATIM Gemini artifact (imported, never edited on disk) against
synthetic SQLite data. Confirms the three named bugs reproduce and reports
any additional signal, per ARTIFACTS_README.md.

All non-ASCII test data is built from chr(0x....) so the source is pure ASCII
and the exact code points are unambiguous.
stdlib only: no tiktoken/NLTK/Presidio needed to test these bugs.
"""
import sys, os, json, hashlib, sqlite3, unicodedata, traceback
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.dirname(HERE)            # parent dir holds the artifact files
sys.path.insert(0, ART)

# code points used as test data (pure ASCII in source)
ACUTE = chr(0x0301)     # COMBINING ACUTE ACCENT
DIAER = chr(0x0308)     # COMBINING DIAERESIS
EACUTE = chr(0x00E9)    # precomposed LATIN SMALL LETTER E WITH ACUTE
EM = chr(0x2003)        # EM SPACE (whitespace, no NFC decomposition)
CAFE_D = "Cafe" + ACUTE         # decomposed: NFC composes to "Caf" + EACUTE
NAIVE_D = "nai" + DIAER + "ve"  # decomposed naive

bar = "=" * 72
print(bar)
print("TIER 2 VERIFICATION: chronicle_failure_profile_loader.py")
print("Testing the verbatim Gemini artifact (not a reconstruction).")
print(bar)


def code_order_normalize(raw_text):
    """Exact replica of the function's pipeline (import fixed), code order."""
    s = raw_text.strip()
    s = " ".join(s.split())
    s = s.replace("\r\n", "\n")
    s = s.encode("utf-8")
    return unicodedata.normalize("NFC", s.decode("utf-8"))


# ---- synthetic DB matching exactly what the function SELECTs ----
docs = {
    "A": "  Hello   World  ",      # leading/trailing + repeated spaces
    "B": "Line one.\r\nLine two.",  # CRLF -> exercises line handling
    "C": CAFE_D,                    # decomposed e+acute -> NFC composes
}
manifest = sorted(
    [{"doc_id": d,
      "sha256": hashlib.sha256(code_order_normalize(t).encode("utf-8")).hexdigest()}
     for d, t in docs.items()],
    key=lambda x: x["doc_id"],
)

conn = sqlite3.connect(":memory:")
c = conn.cursor()
c.execute("""CREATE TABLE chronicle_failure_profiles_v2 (
    profile_id TEXT PRIMARY KEY, signature_hash TEXT,
    temporal_window_start TEXT, temporal_window_end TEXT,
    state_manifest TEXT, ocr_protocol_version TEXT, is_active_audit_profile INTEGER)""")
# NOTE: chronicle_ledger schema is INVENTED here. It is NOT in
# chronicle_failure_profile_ddl.sql, yet the loader SELECTs from it. (Finding B.)
c.execute("CREATE TABLE chronicle_ledger (doc_id TEXT PRIMARY KEY, raw_text TEXT, log_timestamp TEXT)")
c.execute("INSERT INTO chronicle_failure_profiles_v2 VALUES (?,?,?,?,?,?,?)",
          ("PROF-1", "", "2026-05-01T00:00:00", "2026-05-31T00:00:00",
           json.dumps(manifest), "ocr-v1", 1))
for d, t in docs.items():
    c.execute("INSERT INTO chronicle_ledger VALUES (?,?,?)", (d, t, "2026-05-10T12:00:00"))
conn.commit()

import chronicle_failure_profile_loader as loader

# ---- RUN 1: as delivered ----
print("\n[RUN 1] deterministic_load_chronicle_state AS DELIVERED:")
try:
    sig, _ = loader.deterministic_load_chronicle_state(conn, "PROF-1")
    print("  returned:", sig, " >> Bug 1 NOT reproduced.")
except NameError as e:
    print("  NameError:", e)
    print("  >> BUG 1 CONFIRMED (hard runtime crash). There is no implicit import in")
    print("     Python; README's 'probably implicit' is wrong - it always crashes here.")
except Exception as e:
    print("  Unexpected", type(e).__name__, ":", e); traceback.print_exc()

# ---- RUN 2: inject the one missing name, do NOT edit the file ----
loader.unicodedata = unicodedata
print("\n[RUN 2] same call after injecting unicodedata (file unchanged on disk):")
try:
    sig, _ = loader.deterministic_load_chronicle_state(conn, "PROF-1")
    print("  signature_hash:", sig)
    print("  >> Runs to completion. Bugs 2 & 3 do not crash; function otherwise works.")
except Exception as e:
    print("  Unexpected", type(e).__name__, ":", e); traceback.print_exc()

# ---- Bug 2: is the encode/decode roundtrip a noop? ----
print("\n[BUG 2] encode->decode roundtrip vs direct normalize:")
def with_rt(s):    return unicodedata.normalize("NFC", s.encode("utf-8").decode("utf-8"))
def without_rt(s): return unicodedata.normalize("NFC", s)
battery = [CAFE_D, "  a  b  ", "x\r\ny", "A" + EM + EM + "B", EACUTE, NAIVE_D]
alleq = all(with_rt(s) == without_rt(s) for s in battery)
print("  roundtrip == direct on all battery inputs:", alleq,
      "-> noop CONFIRMED" if alleq else "-> NOT a noop")
try:
    with_rt("\ud800")
    print("  [extra] roundtrip survived lone surrogate")
except Exception as e:
    print("  [extra] roundtrip raises", type(e).__name__, "on lone surrogate U+D800")
    print("          >> ADDED FINDING: the 'harmless' roundtrip is not inert - it crashes on")
    print("             lone surrogates. Dropping it (the recommended fix) also removes this path.")

# ---- Bug 3 + line handling: code order vs spec order ----
print("\n[BUG 3] NFC-last (code) vs NFC-first (spec) over a battery:")
def spec_order(t):
    s = unicodedata.normalize("NFC", t)          # NFC FIRST per spec
    s = " ".join(s.strip().split())
    return s.replace("\r\n", "\n")
def code_order(t):
    s = " ".join(t.strip().split())
    s = s.replace("\r\n", "\n")
    return unicodedata.normalize("NFC", s)        # NFC LAST as coded
cases = {
    "combining acute": CAFE_D,
    "multi space": "  a   b  ",
    "CRLF": "Line one.\r\nLine two.",
    "blank lines": "p\n\n\nq",
    "em spaces": "A" + EM + EM + "B",
    "space+combining": "a " + ACUTE + "b",
}
diff = 0
for name, s in cases.items():
    co, so = code_order(s), spec_order(s)
    if co != so: diff += 1
    print(f"  {name:16s} code={co!r:26s} spec={so!r:26s} {'SAME' if co==so else 'DIFFER'}")
print(f"  >> ordering changed the result in {diff}/{len(cases)} cases.")
if diff == 0:
    print("     Bug 3 is behaviorally inert for NFC: NFC has no canonical decomposition that")
    print("     adds/removes whitespace, so it commutes with strip/split/CRLF. The README's")
    print("     rationale ('NFC changes char width affecting whitespace') is an NFKC property.")
    print("     Spec divergence is real on paper; reproducibility risk is smaller than implied.")

# ---- Added finding A: ' '.join(split()) destroys newline structure ----
print("\n[ADDED FINDING A] ' '.join(text.split()) collapses newlines to spaces:")
sample = "Para1 line1.\nPara1 line2.\r\n\r\nPara2."
print("  input:", repr(sample))
print("  code :", repr(code_order(sample)))
print("  >> Every newline becomes a single space. The later .replace('\\r\\n','\\n') is DEAD CODE")
print("     (nothing left to replace). Both vector specs say collapse vertical breaks to a single")
print("     '\\n' (preserve newlines). The code does not implement the spec's line handling, and")
print("     this DOES change the hash. Not among the three named bugs.")

print("\n" + bar)
print("Verification complete.")
print(bar)
