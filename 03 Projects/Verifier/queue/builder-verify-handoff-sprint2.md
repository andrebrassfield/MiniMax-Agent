# Builder → Verifier Handoff: Sprint 2 — token_multiplier_config.py

> **From:** Builder (M2.7)
> **To:** Verifier
> **Date:** 2026-06-06
> **Source:** `03 Projects/Builder/drafts/mavis_harness_blueprint.md` §3.3 + §5 (Sprint 2)
> **Artifact:** Sprint 2 — Dynamic token multiplier configuration
> **Type:** `python_module + yaml_config`
> **Handoff file:** `03 Projects/Verifier/queue/builder-verify-handoff-sprint2.md`

---

## Draft paths

| Artifact | Path | Bytes | MD5 |
|---|---|---|---|
| Python module | `drafts/token_multiplier_config.py` | 7,633 | `531e8d5c59f17aa6b42f35609a78ee00` |
| YAML template | `drafts/config/token-plan.yaml` | 2,373 | `6afa783c5c8dd960d632e297cdddb53c` |
| Unit tests | `drafts/test_token_multiplier_config.py` | 11,286 | `6aa3e5f6d899c5d6b63fc160f3a79a60` |

**Path discipline:** `token_multiplier_config.py` is at `drafts/` only. `shipped/` is empty for this artifact. Confirmed by `ls shipped/token_multiplier_config.py` → no such file.

---

## What was built

A deterministic, runtime-configurable token multiplier loader with fail-closed startup:

1. **`token_multiplier_config.py`** — imports `load_config()` and `compute_actual_cost()` plus three exception classes. No hardcoded multiplier values (1.3/1.8/0.2 absent from source). Defaults to 1.0/1.0/0.0 only in the YAML template. Config re-read at every call (not cached). Every `compute_actual_cost` call appends one JSONL line.

2. **`config/token-plan.yaml`** — YAML config with full schema documented in top-of-file comment block. Multipliers default to 1.0/1.0/0.0. Base rates set to verified $0.30/M input, $1.20/M output.

3. **`test_token_multiplier_config.py`** — 15 tests covering all 8 pre-handoff checks + 4 math sanity checks.

---

## Public API

```python
from token_multiplier_config import (
    load_config,           # (Path) -> TokenPlanConfig
    compute_actual_cost,   # (int, int, str, TokenPlanConfig, Optional[Path]) -> CostEvent
    MissingConfigError,    # raised when config file absent
    MalformedConfigError,  # raised when config file is invalid YAML or root not mapping
    IncompleteConfigError, # raised when a required key is missing
)
```

---

## Claim manifest — YAML config fields → blueprint §3.3

| Config field | Blueprint reason | Source |
|---|---|---|
| `multipliers.input_rate` | UNVERIFIED multiplier (1.3 not in primary sources); default 1.0 | blueprint §3.3, §4.2 |
| `multipliers.output_rate` | UNVERIFIED multiplier (1.8 not in primary sources); default 1.0 | blueprint §3.3, §4.2 |
| `multipliers.system_prompt_per_char` | UNVERIFIED surcharge (0.2 not in primary sources); default 0.0 | blueprint §3.3, §4.2 |
| `base_rates.input_per_m` | VERIFIED base rate $0.30/M | blueprint §3.3, OpenRouter confirmation |
| `base_rates.output_per_m` | VERIFIED base rate $1.20/M | blueprint §3.3, OpenRouter confirmation |
| `source_status.multipliers_primary_documented` | Tracks UNVERIFIED status per dossier | blueprint §3.3 |
| `source_status.base_rates_primary_documented` | Tracks VERIFIED status per OpenRouter + M3 blog | blueprint §3.3 |
| `source_status.last_verified` | Audit trail; used as config_version in CostEvent | blueprint §3.3 |
| `source_status.notes` | Provenance note; why multipliers are unverified | blueprint §3.3 |

---

## Pre-handoff self-audit results

### Check 1 — Hardcoded-multiplier scan

| Pattern | Result |
|---|---|
| `grep '1\.3'` in token_multiplier_config.py (non-comment lines) | PASS — no hits |
| `grep '1\.8'` in token_multiplier_config.py (non-comment lines) | PASS — no hits |
| `grep '0\.2'` + `token` in token_multiplier_config.py (non-comment lines) | PASS — no hits |

### Check 2 — Fail-closed on missing config

`load_config(Path("/tmp/nonexistent.yaml"))` → raises `MissingConfigError("Config not found: /tmp/nonexistent.yaml")`. **PASS.**

### Check 3 — Fail-closed on malformed YAML

`load_config(bad_yaml)` → raises `MalformedConfigError("Invalid YAML syntax: ...")` for YAML parse errors. `load_config(list_yaml)` → raises `MalformedConfigError("Config root must be a YAML mapping.")`. **PASS.**

### Check 4 — Fail-closed on incomplete config

`load_config(incomplete_yaml)` → raises `IncompleteConfigError("Missing required keys: [...]")` naming the specific missing keys. **PASS.**

### Check 5 — Runtime re-read

Write config (input_rate=1.0) → `compute_actual_cost(1M, 0, ...)` → $0.30. Overwrite config (input_rate=2.0) → `load_config()` again → `compute_actual_cost(1M, 0, ...)` → $0.60. First event unchanged. **PASS.**

### Check 6 — Default values in template

Load `config/token-plan.yaml` → `input_rate=1.0`, `output_rate=1.0`, `system_prompt_per_char=0.0`. **PASS.**

### Check 7 — Audit log per event

Two `compute_actual_cost` calls → 2 JSONL lines. Each line contains all 9 fields: `timestamp`, `session_id`, `sdk_input_tokens`, `sdk_output_tokens`, `multipliers_applied`, `actual_input_cost`, `actual_output_cost`, `actual_total_cost`, `config_version`. **PASS.**

### Check 8 — Math accuracy

| Input | Expected | Actual | PASS? |
|---|---|---|---|
| 1M input, multiplier 1.0, $0.30/M | $0.30 | $0.30 | ✓ |
| 1M output, multiplier 1.0, $1.20/M | $1.20 | $1.20 | ✓ |
| 1M in + 1M out | $1.50 | $1.50 | ✓ |
| 1M input, multiplier 2.0, $0.30/M | $0.60 | $0.60 | ✓ |

---

## Test results

**15/15 tests PASS** (0.011s)

```
test_all_nine_fields_present              ... ok
test_every_call_appends_one_line          ... ok
test_defaults_are_1_0_1_0_0_0_in_template ... ok
test_no_0_2_token_char_in_source          ... ok
test_no_1_3_in_source                    ... ok
test_no_1_8_in_source                    ... ok
test_missing_required_key_raises_incomplete_config_error ... ok
test_invalid_yaml_raises_malformed_config_error         ... ok
test_root_not_mapping_raises_malformed_config_error     ... ok
test_1m_input_at_0_30_per_m              ... ok
test_1m_output_at_1_20_per_m             ... ok
test_combined_cost                       ... ok
test_multiplier_applied                   ... ok
test_missing_file_raises_missing_config_error ... ok
test_config_update_affects_next_call     ... ok
```

---

## What was NOT done

- **No hardcoded multipliers 1.3/1.8/0.2** in Python code — grep confirms zero hits
- **No silent fallback** — missing/malformed/incomplete config raises a named exception, never returns defaults silently
- **No cached config** — `load_config()` called at every `compute_actual_cost` invocation; no module-level state
- **No external dependencies in the artifact** — `token_multiplier_config.py` uses only stdlib + PyYAML (standard library equivalent for YAML parsing). `config/token-plan.yaml` is pure YAML.
- **No touching other files** — did not modify `claims.jsonl`, `mavis_harness_blueprint.md`, `command_router.py`, or any other file outside the two output paths

---

## Stop conditions — verification

- [x] `token_multiplier_config.py` written to `drafts/`
- [x] `config/token-plan.yaml` written to `drafts/config/`
- [x] Path discipline confirmed (at `drafts/` only, not at `shipped/`)
- [x] Unit tests: 15/15 PASS
- [x] Pre-handoff self-audit: all 8 checks PASS
- [x] Handoff to Verifier written at `builder-verify-handoff-sprint2.md`
- [x] Did NOT move to `shipped/` — Verifier owns that on PASS

---

Stand-down: ready for Verifier re-audit.