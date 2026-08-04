# Inventory Item Business Object

**Domain:** Masters

**Version:** 1.0

**Status:** Approved

---

# 1. Objective

The Inventory Item Business Object represents a product managed by the business.

It defines **what the business buys, stores, tracks and sells**.

Inventory Item is the central product definition of the AaramBooks platform.

It represents the business concept of a product, independent of individual variants or stock.

---

# 2. Purpose

The purpose of Inventory Item is to maintain a single authoritative definition of every product managed by the business.

Examples:

- Pure Cotton Bedsheet
- Reversible Comforter
- Printed Dohar
- Mattress Protector
- Cushion Cover

Inventory Item represents the product itself.

Individual sellable variants are represented by SKUs.

---

# 3. Business Responsibilities

Inventory Item is responsible for:

- Defining products.
- Maintaining product identity.
- Maintaining product specifications.
- Maintaining product classifications.
- Supporting inventory operations.
- Supporting procurement.
- Supporting reporting.
- Supporting SKU generation.

Inventory Item is **not** responsible for:

- Current Stock.
- Inventory Movements.
- Pricing.
- Purchase Transactions.
- Sales Transactions.

---

# 4. Business Importance

**Priority:** Critical

Inventory Item is the core Business Object of the platform.

Without Inventory Items:

- Procurement cannot occur.
- Inventory cannot exist.
- SKUs cannot exist.
- Reports cannot exist.

---

# 5. Business Rules

### Rule 1

Every Inventory Item shall have one unique Item Code.

---

### Rule 2

Every Inventory Item shall have one Item Name.

---

### Rule 3

Every Inventory Item belongs to exactly one Category.

---

### Rule 4

Every Inventory Item uses one Unit of Measure.

---

### Rule 5

An Inventory Item may have multiple SKUs.

---

### Rule 6

An Inventory Item may have multiple Product Attributes.

---

### Rule 7

Inventory Item Code is immutable.

---

### Rule 8

Inventory Items cannot be deleted once operational transactions exist.

Inactive or Archived status should be used instead.

---

# 6. Business Relationships

## Parent

- Company
- Category
- Unit of Measure

---

## Children

- SKU

---

## Referenced By

- Procurement
- Inventory Intelligence
- Reports
- Search

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

Historical transactions shall always preserve the original Inventory Item.

---

# 8. Business Events

Inventory Item publishes:

- Inventory Item Created
- Inventory Item Updated
- Inventory Item Activated
- Inventory Item Deactivated
- Inventory Item Archived

---

# 9. Business Attributes

| Attribute | Required | Business Type | Editable | Unique | Default |
|-----------|----------|---------------|----------|--------|----------|
| Item Code | Yes | Identifier | No | Yes | None |
| Item Name | Yes | Name | Yes | No | None |
| Description | No | Description | Yes | No | None |
| Category | Yes | Reference | Yes | No | None |
| Unit of Measure | Yes | Reference | Yes | No | None |
| Product Attributes | No | Reference | Yes | No | None |
| HSN Code | No | Identifier | Yes | No | None |
| GST Rate | Yes | Percentage | Yes | No | None |
| Status | Yes | Status | System | No | Active |
| Created On | Yes | Audit | No | No | System |
| Created By | Yes | Audit | No | No | System |
| Updated On | Yes | Audit | No | No | System |
| Updated By | Yes | Audit | No | No | System |

---

# 10. Validation Rules

- Item Code cannot be blank.
- Item Code must be unique.
- Item Name cannot be blank.
- Category is mandatory.
- Unit of Measure is mandatory.
- GST Rate must be valid.
- Status must be:
  - Active
  - Inactive
  - Archived
- Audit attributes are system maintained.

---

# 11. UI Requirements

The Inventory Item module shall provide:

- Item List
- Create Item
- View Item
- Edit Item
- Archive Item
- Search
- Filter by Category
- Filter by Status

---

# 12. API Requirements

The Inventory Item Business Object shall expose APIs for:

- List Inventory Items
- Get Inventory Item
- Create Inventory Item
- Update Inventory Item
- Activate Inventory Item
- Deactivate Inventory Item
- Archive Inventory Item

Deletion API shall not be provided.

---

# 13. Database Considerations

Inventory Item shall exist as an independent Master Data object.

Operational transactions shall reference Inventory Item.

Inventory quantities shall never be stored within Inventory Item.

Current Stock belongs to the Inventory Intelligence Domain.

---

# 14. Implementation Notes

Implementation shall:

- Preserve Item identity.
- Prevent duplicate Item Codes.
- Never store inventory quantities.
- Never store operational transactions.
- Preserve historical references.
- Follow Enterprise Architecture and Engineering Constitution.

---

# 15. Future Scope

Future versions may support:

- Product Images
- Product Documents
- Product Dimensions
- Weight
- Manufacturer
- Barcode
- QR Code
- Product Templates
- AI-generated Product Metadata

---

# 16. Definition of Done

Inventory Item implementation is complete when:

- Business rules are implemented.
- Business attributes are implemented.
- Validation rules are implemented.
- Business events are published.
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