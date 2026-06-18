"""Cost-based model routing by difficulty tier.

Implements the "cost discipline" pillar of Phase 5 Production Hardening:
- Route by difficulty: Haiku for simple, Sonnet for most, Opus for hard reasoning.
- Burn ceiling: hard-stop when estimated cost exceeds the configured ceiling.
- Batch API routing: route non-real-time work to the batch endpoint (50% off).

This module is pure logic (no AIAgent dependency). It is called by the agent
loop at the start of each turn to resolve the effective model/provider.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class CostTier:
    """A single cost-routing tier."""

    def __init__(self, raw: Dict[str, Any]):
        self.name = str(raw.get("name", "")).strip()
        self.description = str(raw.get("description", "")).strip()
        self.patterns = [p.strip() for p in raw.get("patterns", []) if isinstance(p, str) and p.strip()]
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.patterns]
        self.model = str(raw.get("model", "")).strip()
        self.provider = str(raw.get("provider", "")).strip()
        self.base_url = str(raw.get("base_url", "")).strip()
        self.api_key = str(raw.get("api_key", "")).strip()
        self.max_tokens = raw.get("max_tokens")

    def matches(self, user_message: str, conversation_history: List[Dict[str, Any]]) -> bool:
        """Return True if the user message or recent history matches any pattern."""
        text = (user_message or "").strip()
        for pat in self.compiled_patterns:
            if pat.search(text):
                return True
        # Also check the last user message in history if the current one is empty
        if not text and conversation_history:
            for msg in reversed(conversation_history):
                if msg.get("role") == "user":
                    text = str(msg.get("content", "")).strip()
                    for pat in self.compiled_patterns:
                        if pat.search(text):
                            return True
                    break
        return False


class CostRouter:
    """Difficulty-based model router with burn tracking."""

    def __init__(self, config: Dict[str, Any]):
        raw = config or {}
        self.enabled = bool(raw.get("enabled", False))
        self.burn_ceiling_usd = float(raw.get("burn_ceiling_usd", 0.0))
        self.tiers: List[CostTier] = []
        for tier_raw in raw.get("tiers", []):
            if isinstance(tier_raw, dict):
                self.tiers.append(CostTier(tier_raw))
        batch_raw = raw.get("batch", {})
        self.batch_enabled = bool(batch_raw.get("enabled", False)) if isinstance(batch_raw, dict) else False
        self.batch_provider = str(batch_raw.get("provider", "")).strip() if isinstance(batch_raw, dict) else ""
        self.batch_model = str(batch_raw.get("model", "")).strip() if isinstance(batch_raw, dict) else ""
        self.batch_base_url = str(batch_raw.get("base_url", "")).strip() if isinstance(batch_raw, dict) else ""
        self.batch_api_key = str(batch_raw.get("api_key", "")).strip() if isinstance(batch_raw, dict) else ""
        # Session burn accumulator
        self._session_burn_usd = 0.0

    def resolve(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        *,
        is_batch: bool = False,
        default_model: str = "",
        default_provider: str = "",
        default_base_url: str = "",
        default_api_key: str = "",
    ) -> Tuple[str, str, str, str, Optional[int]]:
        """Return the effective (model, provider, base_url, api_key, max_tokens) for this turn.

        If no tier matches, returns the defaults. If cost_routing is disabled,
        returns the defaults immediately.
        """
        if not self.enabled:
            return default_model, default_provider, default_base_url, default_api_key, None

        # Batch API takes precedence for non-real-time work
        if is_batch and self.batch_enabled and self.batch_model:
            return (
                self.batch_model,
                self.batch_provider or default_provider,
                self.batch_base_url or default_base_url,
                self.batch_api_key or default_api_key,
                None,
            )

        for tier in self.tiers:
            if tier.matches(user_message, conversation_history or []):
                if tier.model:
                    return (
                        tier.model,
                        tier.provider or default_provider,
                        tier.base_url or default_base_url,
                        tier.api_key or default_api_key,
                        tier.max_tokens,
                    )
                else:
                    # Tier matched but no override model → still return default,
                    # but let the caller know a tier was hit (for logging/metrics).
                    return default_model, default_provider, default_base_url, default_api_key, tier.max_tokens

        return default_model, default_provider, default_base_url, default_api_key, None

    def add_burn(self, estimated_usd: float) -> bool:
        """Add estimated burn and return True if still under ceiling.

        If burn_ceiling_usd is 0.0, always returns True.
        """
        if self.burn_ceiling_usd <= 0.0:
            return True
        self._session_burn_usd += estimated_usd
        if self._session_burn_usd > self.burn_ceiling_usd:
            logger.warning(
                "Burn ceiling hit: %.4f / %.4f USD",
                self._session_burn_usd,
                self.burn_ceiling_usd,
            )
            return False
        return True

    def current_burn(self) -> float:
        return self._session_burn_usd


def load_cost_router() -> CostRouter:
    """Load the cost router from config.yaml."""
    try:
        from hermes_cli.config import load_config
        cfg = load_config()
        return CostRouter(cfg.get("cost_routing", {}))
    except Exception:
        logger.debug("Cost routing config load failed, using disabled router", exc_info=True)
        return CostRouter({})
