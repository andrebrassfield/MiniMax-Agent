"""
token_multiplier_config — Dynamic token multiplier loader for the Mavis Harness.

Every multiplier value comes from config/token-plan.yaml at runtime.
Python code contains ONLY the fail-closed defaults (1.0/1.0/0.0) and logic.

Schema contract (see also config/token-plan.yaml):
    multipliers:
        input_rate: float          # applied to sdk_input_tokens
        output_rate: float         # applied to sdk_output_tokens
        system_prompt_per_char: float  # per-char surcharge (currently 0.0 default)
    base_rates:
        input_per_m: float         # USD per 1M input tokens
        output_per_m: float        # USD per 1M output tokens
    source_status:
        multipliers_primary_documented: bool
        base_rates_primary_documented: bool
        last_verified: str         # ISO date string
        notes: str

Cost formula:
    actual_input_cost  = sdk_input_tokens  * input_rate  * input_per_m / 1_000_000
    actual_output_cost = sdk_output_tokens * output_rate * output_per_m / 1_000_000
    actual_total       = actual_input_cost + actual_output_cost
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import json

import yaml  # type: ignore


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class MissingConfigError(Exception):
    """Raised when the config file does not exist."""
    pass


class MalformedConfigError(Exception):
    """Raised when the config file is present but contains invalid YAML."""
    pass


class IncompleteConfigError(Exception):
    """Raised when the config YAML is valid but missing a required key."""
    pass


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class TokenPlanConfig:
    # Multipliers (all 1.0 by default — unverified in primary sources)
    input_rate: float
    output_rate: float
    system_prompt_per_char: float
    # Base rates (verified)
    input_per_m: float
    output_per_m: float
    # Source metadata
    multipliers_primary_documented: bool
    base_rates_primary_documented: bool
    last_verified: str
    notes: str


@dataclass
class CostEvent:
    """One accounting event, emitted as a JSONL log entry."""
    timestamp: str
    session_id: str
    sdk_input_tokens: int
    sdk_output_tokens: int
    multipliers_applied: dict
    actual_input_cost: float
    actual_output_cost: float
    actual_total_cost: float
    config_version: str


# ---------------------------------------------------------------------------
# Default log path (chief's workspace — see handoff §Audit log per event)
# ---------------------------------------------------------------------------

DEFAULT_LOG_PATH = Path.home() / ".mavis" / "agents" / "mavis" / "workspace" / "token-accounting.jsonl"


# ---------------------------------------------------------------------------
# Config loader — runtime re-read, fail-closed
# ---------------------------------------------------------------------------

def load_config(config_path: Path) -> TokenPlanConfig:
    """
    Load and validate token-plan.yaml. Fails closed on any error.

    This function is called at every compute_actual_cost invocation — NOT
    cached at module import — so config updates take effect immediately.
    """
    if not config_path.exists():
        raise MissingConfigError(f"Config not found: {config_path}")

    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise MalformedConfigError(f"Invalid YAML syntax: {e}")

    if not isinstance(raw, dict):
        raise MalformedConfigError("Config root must be a YAML mapping.")

    multipliers = raw.get("multipliers", {})
    base_rates = raw.get("base_rates", {})
    source_status = raw.get("source_status", {})

    # Enumerate every required key so IncompleteConfigError names them precisely
    required = [
        ("multipliers.input_rate",            multipliers.get("input_rate")),
        ("multipliers.output_rate",           multipliers.get("output_rate")),
        ("multipliers.system_prompt_per_char", multipliers.get("system_prompt_per_char")),
        ("base_rates.input_per_m",            base_rates.get("input_per_m")),
        ("base_rates.output_per_m",           base_rates.get("output_per_m")),
    ]
    missing = [name for name, value in required if value is None]
    if missing:
        raise IncompleteConfigError(f"Missing required keys: {missing}")

    return TokenPlanConfig(
        input_rate=float(multipliers["input_rate"]),
        output_rate=float(multipliers["output_rate"]),
        system_prompt_per_char=float(multipliers["system_prompt_per_char"]),
        input_per_m=float(base_rates["input_per_m"]),
        output_per_m=float(base_rates["output_per_m"]),
        multipliers_primary_documented=bool(source_status.get("multipliers_primary_documented", False)),
        base_rates_primary_documented=bool(source_status.get("base_rates_primary_documented", False)),
        last_verified=str(source_status.get("last_verified", "")),
        notes=str(source_status.get("notes", "")),
    )


# ---------------------------------------------------------------------------
# Cost computation — every call re-reads the config and emits a JSONL log
# ---------------------------------------------------------------------------

def compute_actual_cost(
    sdk_input_tokens: int,
    sdk_output_tokens: int,
    session_id: str,
    config: TokenPlanConfig,
    log_path: Optional[Path] = None,
) -> CostEvent:
    """
    Compute the actual cost with multipliers applied and log every event.

    Arguments:
        sdk_input_tokens:  token count reported by the SDK (pre-multiplier)
        sdk_output_tokens: token count reported by the SDK (pre-multiplier)
        session_id:        identifier of the session being charged
        config:            a TokenPlanConfig loaded by load_config()
        log_path:          path for the JSONL audit log; defaults to DEFAULT_LOG_PATH

    Returns:
        CostEvent with all computed fields.

    Side effect:
        One JSONL line is appended to log_path (if provided).
    """
    actual_input_cost = (
        sdk_input_tokens * config.input_rate * config.input_per_m / 1_000_000
    )
    actual_output_cost = (
        sdk_output_tokens * config.output_rate * config.output_per_m / 1_000_000
    )
    actual_total = actual_input_cost + actual_output_cost

    event = CostEvent(
        timestamp=datetime.now(timezone.utc).isoformat(),
        session_id=session_id,
        sdk_input_tokens=sdk_input_tokens,
        sdk_output_tokens=sdk_output_tokens,
        multipliers_applied={
            "input_rate":             config.input_rate,
            "output_rate":            config.output_rate,
            "system_prompt_per_char": config.system_prompt_per_char,
        },
        actual_input_cost=actual_input_cost,
        actual_output_cost=actual_output_cost,
        actual_total_cost=actual_total,
        # Use last_verified as the config version string
        config_version=config.last_verified or "unversioned",
    )

    target = log_path if log_path is not None else DEFAULT_LOG_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")

    return event