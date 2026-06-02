"""
Synthetic compression benchmark.

Headroom's published numbers show 92% savings on code search results.
The deterministic compression layer should approach those numbers on
similar inputs. This script simulates the workload and measures.
"""
import sys
from pathlib import Path

# Allow running from either the project root or the tests/ directory
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # project root (where intake/ lives)

from intake import compress  # noqa: E402

# Simulate a code-search-result workload (similar to Headroom's benchmark)
# 50 search-result blocks with the same structure repeated
code_results = []
files = ["router.py", "curator.py", "self_card.py", "healer.py"]
ops = ["drop", "review", "list", "explain"]

for i in range(50):
    fn = files[i % 4]
    op = ops[i % 4]
    code_results.append(
        f"""
### match #{i+1} — src/agents/{fn}:{100 + i * 7}
**Score:** {round(0.95 - i * 0.01, 3)}
**File:** /Users/me/proj/src/agents/{fn}
**Symbol:** def handle_{op}(self, intake_id: str)

```python
def handle_{op}(self, intake_id: str) -> dict:
    \"\"\"Handle the {op} operation for the direct-intake MCP.\"\"\"
    record = self.store.get(intake_id)
    if not record:
        return {{"error": f"intake_id not found: {{intake_id}}"}}
    return record.to_dict()
```
"""
    )

text = "\n".join(code_results)
print(f"Input: {len(text)} chars, ~{compress.estimate_tokens(text)} tokens (heuristic)")

c = compress.compress(text, aggressive=True)
print(f"Compressed: {len(c.text)} chars, ~{c.compressed_tokens} tokens (heuristic)")
print(f"Ratio: {c.compression_ratio:.3f} ({(1.0 - c.compression_ratio) * 100:.1f}% savings)")
print(f"Algorithms: {c.algorithms_applied}")
print()

# Verify content preservation
print("Content preservation check:")
print(f"  'router.py' present: {'router.py' in c.text}")
print(f"  'handle_drop' present: {'handle_drop' in c.text}")
print(f"  'Score' present: {'Score' in c.text}")
print(f"  'intake_id' present: {'intake_id' in c.text}")
print(f"  Python def preserved: {'def handle_drop' in c.text or 'def handle_' in c.text}")
print()

# CCR round-trip
store = compress.CCRStore()
store.put(text)
assert store.get(c.ccr_hash) == text
print("CCR: original retrievable by hash: OK")
print(f"CCR hash: {c.ccr_hash[:16]}...")
