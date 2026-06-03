# Tests

> The Researcher is testable. Each test maps to a contract from SOUL.md / AGENTS.md.

See `RESEARCHER-GOD-PROMPT.md` and `RESEARCHER-TEST.md` in this directory for the master onboarding prompt and the test scenarios Andre will use to onboard and verify the Researcher.

## Local test scripts (to be built)

- `tests/test_schema.py` — validates that knowledge/*.jsonl parses
- `tests/test_handoff_shape.py` — validates that queue/*-handoff.md follows schema
- `tests/test_health_check.py` — validates health check produces PASS/DEGRADED/FAIL
- `tests/test_source_balance.py` — validates that social % stays under threshold
- `tests/test_loop_idempotency.py` — validates re-running REFRESH does not duplicate records
