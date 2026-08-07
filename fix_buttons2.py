with open("frontend/src/components/products/QuickInventoryActionCard.tsx", "r") as f:
    content = f.read()

content = content.replace(
    'Add Stock\n            </Button>',
    'Increase Stock\n            </Button>'
)

with open("frontend/src/components/products/QuickInventoryActionCard.tsx", "w") as f:
    f.write(content)
