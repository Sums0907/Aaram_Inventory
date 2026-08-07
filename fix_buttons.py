with open("frontend/src/components/products/QuickInventoryActionCard.tsx", "r") as f:
    content = f.read()

content = content.replace(
    'Manual Adjustment\n            </Button>',
    'Add Stock\n            </Button>'
)

with open("frontend/src/components/products/QuickInventoryActionCard.tsx", "w") as f:
    f.write(content)
