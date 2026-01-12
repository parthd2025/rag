#!/usr/bin/env python3
"""Debug script to check chunks and New York data."""
import sys
sys.path.insert(0, 'D:\\RAG')

from backend.vectorstore import FAISSVectorStore

vs = FAISSVectorStore()
print(f"Total chunks in index: {len(vs.chunks)}")

# Get unique documents
docs = set(m.get("source_doc") for m in vs.metadata)
print(f"Documents: {docs}")

# Count New York occurrences and extract sales values
ny_rows = []
for i, chunk in enumerate(vs.chunks):
    if "New York" in chunk:
        # Extract rows with New York
        lines = chunk.split("\n")
        for line in lines:
            if "New York" in line:
                ny_rows.append(line.strip())

print(f"\nTotal rows with 'New York': {len(ny_rows)}")
print("\n--- First 5 New York rows ---")
for row in ny_rows[:5]:
    print(row)

# Try to extract sales values
print("\n--- Attempting to extract Sales column ---")
sales_total = 0
for row in ny_rows:
    # Try to parse the row format: [R#] ID | Name | Gender | Supervisor | Sales | ...
    parts = row.split("|")
    if len(parts) >= 5:
        try:
            # Sales appears to be 5th field (index 4)
            sales_str = parts[4].strip()
            sales = int(sales_str)
            sales_total += sales
            print(f"  Row: Sales = {sales}")
        except (ValueError, IndexError) as e:
            pass

print(f"\n=== CALCULATED TOTAL SALES FOR NEW YORK: {sales_total} ===")

# Show one full chunk
print("\n--- Full Sample Chunk (first with New York) ---")
for i, chunk in enumerate(vs.chunks):
    if "New York" in chunk:
        print(chunk[:1000])
        break
