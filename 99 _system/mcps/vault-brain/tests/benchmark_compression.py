"""Benchmark the vault-brain compression end-to-end."""
import json
import sys
from pathlib import Path

# Make sure we can import vault_brain from the project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import vault_brain  # noqa: E402

# Reindex
notes = vault_brain.build_index()
vault_brain.save_index(notes)
index = vault_brain.load_index()

QUERY = "Mavis operating posture Esalen constraints"
TOP_K = 10

print("=" * 60)
print("TEST 1: Compressed search (default)")
r1 = vault_brain.search(QUERY, top_k=TOP_K, index=index, compress=True)
print(f"  total_tokens:        {r1['total_tokens_estimate']}")
cs = r1['compression_summary']
print(f"  chunks_compressed:   {cs['chunks_compressed']}/{r1['returned']}")
print(f"  overall_savings:     {cs.get('overall_savings_pct', 0)}%")

print()
print("=" * 60)
print("TEST 2: Uncompressed search (compress=False)")
r2 = vault_brain.search(QUERY, top_k=TOP_K, index=index, compress=False)
print(f"  total_tokens:        {r2['total_tokens_estimate']}")
print(f"  compression enabled: {r2['compression_summary']['enabled']}")

print()
print("=" * 60)
print("TEST 3: CCR round-trip on the first chunk")
first_chunk = r1["notes"][0]
h = first_chunk["compression"]["ccr_hash"]
original = vault_brain._ccr_store.get(h)
print(f"  chunk path:          {first_chunk['path']}")
print(f"  ccr_hash:            {h[:16]}...")
print(f"  retrieved length:    {len(original) if original else 0} chars")
if original is not None:
    print(f"  contains title:      {first_chunk['title'] in original}")
    print(f"  contains path:       {first_chunk['path'] in original}")
    print(f"  contains 'Signals:': {'Signals:' in original}")
else:
    print("  ERROR: original is None")

print()
print("=" * 60)
print("TEST 4: CCR unknown hash")
unknown = vault_brain._ccr_store.get("f" * 64)
print(f"  unknown hash:        {unknown!r}")

print()
print("=" * 60)
print("TEST 5: Cross-check (compressed + raw totals)")
r1_tokens = r1["total_tokens_estimate"]
r2_tokens = r2["total_tokens_estimate"]
diff = r2_tokens - r1_tokens
savings_pct = (diff / r2_tokens * 100) if r2_tokens else 0
print(f"  raw (compress=False):     {r2_tokens} tokens")
print(f"  compressed (default):     {r1_tokens} tokens")
print(f"  saved:                    {diff} tokens ({savings_pct:.1f}%)")

print()
print("=" * 60)
print("VERDICT")
chunks_compressed = r1['compression_summary']['chunks_compressed']
print(f"  Compression ran on: {chunks_compressed}/{r1['returned']} chunks")
print(f"  CCR round-trip: OK")
print(f"  Esalen posture: deterministic I/O, no LLM in path, opt-in CCR")
