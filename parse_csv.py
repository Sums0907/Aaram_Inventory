import pandas as pd
df = pd.read_csv('input/Order Reconciliation Report.csv', skiprows=2)

target_sku = 'KD-RJ-RJP-KDB'
sku_df = df[df['SKU Code'].str.strip() == target_sku]

counts = sku_df['Order Status'].str.strip().str.upper().value_counts().to_dict()

statuses = [
    'DELIVERED', 
    'CANCELLED_INITIATED', 
    'RTO_ACKNOWLEDGED', 
    'RTO_INITIATED', 
    'RETURN', 
    'RTO_DELIVERED'
]

print(f"\nOrder Status counts for SKU: {target_sku}")
for s in statuses:
    print(f"{s}: {counts.get(s, 0)}")

# Also print all found statuses just in case spelling differs
print("\nAll found statuses for this SKU:")
for k, v in counts.items():
    print(f"{k}: {v}")

