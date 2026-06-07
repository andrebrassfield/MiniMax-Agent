# Handoff — Mavis (chief) → Builder (Sprint 2: token_multiplier_config.py)

> Source: `03 Projects/Builder/drafts/mavis_harness_blueprint.md` §3.3 (Dynamic token multiplier configuration) + §5 (Build sequencing, Sprint 2)
> Phase: 3 — Operation: Cognitive Architecture, Sprint 2
> Authored: 2026-06-06 by Mavis (chief of staff)
> Sprint 1 was verified PASS (command_router.py shipped 2026-06-06). Sprint 2 is independent and can run in parallel with Sprint 1's Verifier audit.

## Strategic context

The Token Plan multipliers (1.3x input / 1.8x output / 0.2 token/char surcharge) are UNVERIFIED in primary sources. We CANNOT hardcode them. Per blueprint §3.3, the architecture must:
- Read multipliers from a config file at runtime
- Default to 1.0/1.0/0.0 (verified base rates only) until a primary source confirms the multipliers
- Log every accounting event with the multipliers used
- Fail closed if the config is missing

Sprint 1 closed the framework-drift gap (regex pre-filter). Sprint 2 closes the production-accounting gap (runtime-configurable multipliers). Together they immunize the harness against the two highest-impact hallucination vectors identified by the dossier.

## Task

Build a **deterministic, runtime-configurable token multiplier loader** that reads a YAML config file at every accounting event, applies the multipliers to the SDK-reported `total_tokens`, computes the actual cost, and logs every event. NO HARDCODED MULTIPLIER VALUES in the Python code.

- **Artifact 1:** `03 Projects/Builder/drafts/token_multiplier_config.py` — the loader module
- **Artifact 2:** `config/token-plan.yaml` — the YAML template (with full schema documentation)
- **Render target:** A Python module importable as `from token_multiplier_config import compute_actual_cost, load_config, MissingConfigError`. A YAML file the module reads. The module MUST fail closed if the YAML is missing or malformed.

## Hard constraints

### 1. No hardcoded multiplier values

**Every multiplier value comes from the YAML config at runtime.** The Python code contains ONLY:
- Default values of `1.0` (input), `1.0` (output), `0.0` (system-prompt surcharge) — these are the "verified base rates only" defaults
- Logic to read the YAML, validate it, apply it

The Verifier will grep the Python file for the literal strings `1.3`, `1.8`, `0.2 token/char` — any hit is a FAIL.

### 2. Fail-closed startup

If the config file is missing → raise `MissingConfigError` and refuse to compute. No silent fallback to defaults.

If the config file is malformed (invalid YAML, missing required keys, wrong types) → raise `MalformedConfigError` with a descriptive message. No silent fallback.

If a required multiplier key is missing from the YAML → raise `IncompleteConfigError`. The config must explicitly state every multiplier, even if it's the safe default.

### 3. Runtime re-read

The config is read at every `compute_actual_cost` call — NOT cached at module import. This means a config update takes effect on the next accounting event without code change. The Verifier will test this by writing a config, computing a cost, updating the config, and re-computing.

### 4. Audit log per event

Every `compute_actual_cost` call emits a structured log entry with:
- Timestamp (ISO8601 with timezone)
- Session ID (passed as parameter)
- SDK-reported input_tokens, output_tokens
- Multipliers applied (input_rate, output_rate, system_prompt_per_char)
- Computed actual cost
- Config version (a hash or version string from the YAML)

Log format: JSONL to a configured path. Default log path: `~/.mavis/agents/mavis/workspace/token-accounting.jsonl` (chief's workspace, because this is chief-side accounting).

### 5. Schema as code

The YAML schema is documented IN the YAML file itself (top-of-file comment block). The Python module has matching docstring. A future Verifier can read either and know the contract.

## Suggested module shape

```python
# token_multiplier_config.py
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import yaml

class MissingConfigError(Exception): pass
class MalformedConfigError(Exception): pass
class IncompleteConfigError(Exception): pass

@dataclass
class TokenPlanConfig:
    input_rate: float
    output_rate: float
    system_prompt_per_char: float
    input_per_m: float
    output_per_m: float
    multipliers_primary_documented: bool
    last_verified: str
    notes: str

def load_config(config_path: Path) -> TokenPlanConfig:
    """Load and validate the token-plan.yaml. Fail closed on any error."""
    if not config_path.exists():
        raise MissingConfigError(f"Config not found: {config_path}")
    try:
        raw = yaml.safe_load(config_path.read_text(encoding='utf-8'))
    except yaml.YAMLError as e:
        raise MalformedConfigError(f"Invalid YAML: {e}")
    
    multipliers = raw.get("multipliers", {})
    base_rates = raw.get("base_rates", {})
    source_status = raw.get("source_status", {})
    
    required = [
        ("multipliers.input_rate", multipliers.get("input_rate")),
        ("multipliers.output_rate", multipliers.get("output_rate")),
        ("multipliers.system_prompt_per_char", multipliers.get("system_prompt_per_char")),
        ("base_rates.input_per_m", base_rates.get("input_per_m")),
        ("base_rates.output_per_m", base_rates.get("output_per_m")),
    ]
    missing = [k for k, v in required if v is None]
    if missing:
        raise IncompleteConfigError(f"Missing required keys: {missing}")
    
    return TokenPlanConfig(
        input_rate=float(multipliers["input_rate"]),
        output_rate=float(multipliers["output_rate"]),
        system_prompt_per_char=float(multipliers["system_prompt_per_char"]),
        input_per_m=float(base_rates["input_per_m"]),
        output_per_m=float(base_rates["output_per_m"]),
        multipliers_primary_documented=bool(source_status.get("multipliers_primary_documented", False)),
        last_verified=str(source_status.get("last_verified", "")),
        notes=str(source_status.get("notes", ""))
    )

@dataclass
class CostEvent:
    timestamp: str
    session_id: str
    sdk_input_tokens: int
    sdk_output_tokens: int
    multipliers_applied: dict
    actual_input_cost: float
    actual_output_cost: float
    actual_total_cost: float
    config_version: str

def compute_actual_cost(
    sdk_input_tokens: int,
    sdk_output_tokens: int,
    session_id: str,
    config: TokenPlanConfig,
    log_path: Optional[Path] = None
) -> CostEvent:
    """Compute the actual cost with multipliers applied. Log every event."""
    actual_input_cost = (
        sdk_input_tokens
        * config.input_rate
        * config.input_per_m
        / 1_000_000
    )
    actual_output_cost = (
        sdk_output_tokens
        * config.output_rate
        * config.output_per_m
        / 1_000_000
    )
    actual_total = actual_input_cost + actual_output_cost
    
    event = CostEvent(
        timestamp=<now>,
        session_id=session_id,
        sdk_input_tokens=sdk_input_tokens,
        sdk_output_tokens=sdk_output_tokens,
        multipliers_applied={
            "input_rate": config.input_rate,
            "output_rate": config.output_rate,
            "system_prompt_per_char": config.system_prompt_per_char
        },
        actual_input_cost=actual_input_cost,
        actual_output_cost=actual_output_cost,
        actual_total_cost=actual_total,
        config_version=<hash of config or last_verified>
    )
    
    # Append to log
    if log_path:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(event), ensure_ascii=False) + '\n')
    
    return event
```

## Suggested YAML template

```yaml
# Token Plan multipliers — UNVERIFIED in primary sources as of 2026-06-05.
# Per dossier-audit-2026-06-05-m2.7-verifier.md, the 1.3x/1.8x/0.2 surcharge
# numbers are NOT in the official Token Plan FAQ or Rate Limits page.
# Until a primary source confirms, multipliers default to 1.0/1.0/0.0.
# Update ONLY after primary-source confirmation.
multipliers:
  input_rate: 1.0            # UNVERIFIED, default 1.0
  output_rate: 1.0           # UNVERIFIED, default 1.0
  system_prompt_per_char: 0.0  # UNVERIFIED, default 0.0

# Base rates — VERIFIED via OpenRouter + M3 launch blog.
base_rates:
  input_per_m: 0.30          # USD per 1M input tokens
  output_per_m: 1.20         # USD per 1M output tokens

# Source status — what we know about where these numbers came from.
source_status:
  multipliers_primary_documented: false
  base_rates_primary_documented: true
  last_verified: 2026-06-05
  notes: >
    Per dossier UNVERIFIED status; primary source (platform.minimax.io/docs/token-plan/faq)
    does not contain multiplier language. Apply only verified base rates until
    primary-source confirmation.
```

## Pre-handoff self-audit (run before sending to Verifier)

1. **Hardcoded-multiplier scan** — `grep -E '1\.3|1\.8|0\.2.*token' drafts/token_multiplier_config.py` — zero hits required.
2. **Fail-closed test** — missing config file raises `MissingConfigError`, not a silent default.
3. **Malformed-config test** — invalid YAML raises `MalformedConfigError` with a descriptive message.
4. **Incomplete-config test** — missing required key raises `IncompleteConfigError`.
5. **Runtime re-read test** — update the config between two `compute_actual_cost` calls; verify the second call uses the new values.
6. **Default-values test** — fresh install with no config edits: input/output multipliers are 1.0/1.0, surcharge 0.0.
7. **Audit log test** — every `compute_actual_cost` call appends one JSONL line with all 9 fields.
8. **Math test** — known inputs produce known costs (e.g., 1M input tokens at $0.30/M = $0.30; 1M output at $1.20/M = $1.20).

## Handoff to Verifier

Write to: `03 Projects/Verifier/queue/builder-verify-handoff-sprint2.md` (NEW FILE — different from the Sprint 1 handoff which lives at `builder-verify-handoff.md`).

Include:
- Source blueprint path + section
- Draft paths (artifact + YAML template)
- Artifact type (`python_module + yaml_config`)
- Language(s) used
- Claim manifest (every config field → blueprint §3.3 reason code)
- Hygiene self-audit (results of the 8 pre-handoff checks)
- Test results
- What you did NOT do (no hardcoded multipliers, no silent defaults, no cached config)

Then report back here with: (1) draft paths, (2) file sizes, (3) test results, (4) any issues. Do NOT move to `shipped/`.

## Stop conditions

- [ ] `token_multiplier_config.py` written
- [ ] `config/token-plan.yaml` written (in `03 Projects/Builder/drafts/config/` or appropriate path)
- [ ] Unit tests pass (at least 8 per the pre-handoff checks)
- [ ] Pre-handoff self-audit (8 checks) all clean
- [ ] Handoff to Verifier (`builder-verify-handoff-sprint2.md`) with claim manifest
- [ ] Did NOT move to `shipped/`

You are done. The Verifier will route PASS → `shipped/` or FAIL → redlines back to you.
