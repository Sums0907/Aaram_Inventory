# SKU Business Object

**Domain:** Masters

**Version:** 1.0

**Status:** Approved

---

# 1. Objective

The SKU (Stock Keeping Unit) Business Object represents the smallest identifiable and sellable variant of an Inventory Item.

A SKU is the unit against which inventory is maintained, purchases are recorded and sales are processed.

Every stock movement within AaramBooks shall occur against a SKU.

---

# 2. Purpose

The purpose of SKU is to represent individual product variants.

Examples:

Inventory Item

Pure Cotton Bedsheet

SKUs

- King - Blue
- King - Grey
- Queen - Blue
- Queen - Grey

Although these belong to the same Inventory Item, each SKU represents an independent stock item.

---

# 3. Business Responsibilities

SKU is responsible for:

- Representing sellable product variants.
- Maintaining unique product identity.
- Supporting inventory tracking.
- Supporting procurement.
- Supporting stock valuation.
- Supporting reporting.

SKU is **not** responsible for:

- Product definition.
- Category definition.
- Product attributes.
- Inventory calculations.

---

# 4. Business Importance

**Priority:** Critical

SKU is the operational inventory unit.

Without SKU:

- Inventory cannot be tracked accurately.
- Procurement quantities cannot be maintained.
- Product variants cannot exist.
- Warehouse stock cannot be calculated.

---

# 5. Business Rules

### Rule 1

Every SKU shall belong to exactly one Inventory Item.

---

### Rule 2

Every SKU shall have one unique SKU Code.

---

### Rule 3

A SKU represents one unique combination of Product Attribute Values.

---

### Rule 4

Two SKUs under the same Inventory Item cannot have identical attribute combinations.

---

### Rule 5

SKU Code is immutable.

---

### Rule 6

A SKU cannot be deleted after operational transactions exist.

Inactive or Archived status should be used instead.

---

### Rule 7

Historical transactions shall always preserve the original SKU.

---

# 6. Business Relationships

## Parent

- Company
- Inventory Item

---

## References

- Warehouse
- Procurement
- Inventory Intelligence
- Reports

---

# 7. Business Lifecycle

```
Create

↓

Configure

↓

Active

↓

Update

↓

Inactive

↓

Archive

↓

Historical Preservation
```

---

# 8. Business Events

SKU publishes:

- SKU Created
- SKU Updated
- SKU Activated
- SKU Deactivated
- SKU Archived

---

# 9. Business Attributes

| Attribute | Required | Type | Editable | Unique |
|------------|----------|------|----------|--------|
| SKU Code | Yes | Identifier | No | Yes |
| SKU Name | Yes | Name | Yes | No |
| Inventory Item | Yes | Reference | No | No |
| Attribute Values | Yes | Reference | Yes | No |
| Barcode | No | Identifier | Yes | Yes |
| HSN Code | No | Identifier | Yes | No |
| GST Rate | Yes | Percentage | Yes | No |
| Status | Yes | Status | System | No |
| Created On | Yes | Audit | No | No |
| Created By | Yes | Audit | No | No |
| Updated On | Yes | Audit | No | No |
| Updated By | Yes | Audit | No | No |

---

# 10. Validation Rules

- SKU Code cannot be blank.
- SKU Code must be unique.
- Inventory Item is mandatory.
- Attribute combination must be unique within an Inventory Item.
- Barcode, if provided, should be unique.
- Status must be Active, Inactive or Archived.

---

# 11. UI Requirements

The SKU module shall provide:

- SKU List
- Create SKU
- Edit SKU
- View SKU
- Archive SKU
- Search by SKU Code
- Search by SKU Name
- Filter by Inventory Item
- Filter by Status

---

# 12. API Requirements

The SKU Business Object shall expose APIs for:

- List SKUs
- Get SKU
- Create SKU
- Update SKU
- Activate SKU
- Deactivate SKU
- Archive SKU

Deletion API shall not be provided.

---

# 13. Database Considerations

SKU shall exist as an independent Master Data object.

All operational transactions shall reference SKU rather than Inventory Item.

Inventory balances shall always be maintained at SKU level.

---

# 14. Implementation Notes

Implementation shall:

- Maintain one unique SKU Code.
- Prevent duplicate attribute combinations.
- Preserve historical references.
- Never delete operational SKUs.
- Follow the Enterprise Architecture and Engineering Constitution.

---

# 15. Future Scope

Future versions may support:

- Marketplace SKU
- Vendor SKU
- Multiple Barcodes
- Bundle SKU
- Composite SKU
- Seasonal SKU
- Digital Products

---

# 16. Definition of Done

SKU implementation is complete when:

- Business rules are implemented.
- Business attributes are implemented.
- Validation rules are implemented.
- Business events are implemented.
- Database schema is implemented.
- APIs are implemented.
- UI is implemented.
- Tests pass.
- Documentation is updated.

---

# 17. References

This Business Object shall comply with:

- Business Model
- System Architecture
- Event Model
- Information Model
- Masters Domain README
- Engineering Constitution