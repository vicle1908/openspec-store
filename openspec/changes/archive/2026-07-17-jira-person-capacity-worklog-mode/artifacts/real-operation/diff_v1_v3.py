"""Compare the v1 (legacy) and v3 (new) Person Capacity tabs."""
import json

with open('/tmp/person_capacity_before.json') as f:
    v1 = json.load(f)
with open('/tmp/person_capacity_after.json') as f:
    v3 = json.load(f)

print(f"v1: {len(v1)} rows, {sum(1 for r in v1 if any(c for c in r))} non-empty")
print(f"v3: {len(v3)} rows, {sum(1 for r in v3 if any(c for c in r))} non-empty")

# Extract v1 metric block
v1_metrics = {}
for row in v1[1:7]:
    if len(row) >= 2:
        v1_metrics[row[0]] = row[1]
print(f"\nv1 metrics: {v1_metrics}")

# Extract v3 metric block
v3_metrics = {}
for row in v3[1:6]:
    if len(row) >= 2:
        v3_metrics[row[0]] = row[1]
print(f"v3 metrics: {v3_metrics}")

# Header comparison
v1_header = next((r for r in v1 if r and r[0] == 'No.'), None)
v3_header = next((r for r in v3 if r and r[0] == 'No.'), None)
print(f"\nv1 header ({len(v1_header)} cols): {v1_header}")
print(f"\nv3 header ({len(v3_header)} cols): {v3_header}")

# Row deltas: v1 has 33 active rows, v3 has 26 active rows
v1_active_count = 0
for row in v1[10:]:
    if row and row[0].isdigit() and int(row[0]) > v1_active_count:
        v1_active_count = int(row[0])
v3_active_count = 0
for row in v3[8:]:
    if row and row[0].isdigit() and int(row[0]) > v3_active_count:
        v3_active_count = int(row[0])
print(f"\nactive rows: v1={v1_active_count}, v3={v3_active_count}")
print(f"  v1 → v3 delta: -{v1_active_count - v3_active_count} members (members without worklogs moved to reconciliation)")

# Reconciliation comparison
print("\nv1 reconciliation: 0 blocks (legacy v1 had no reconciliation block)")
print("v3 reconciliation:")
for row in v3[35:]:
    if row and len(row) >= 1 and row[0] != 'RECONCILIATION' and row[0] != 'Metric':
        print(f"  {row[0]}: count={row[1] if len(row) > 1 else '?'}, samples={row[2] if len(row) > 2 else ''}")
