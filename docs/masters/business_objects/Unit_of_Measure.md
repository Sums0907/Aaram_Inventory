# Unit of Measure Business Object

**Domain:** Masters

**Version:** 1.0

**Status:** Approved

---

# 1. Objective

The Unit of Measure (UOM) Business Object represents the standard unit in which business quantities are expressed throughout the AaramBooks platform.

It ensures that all quantities are measured consistently across inventory, procurement, operations and reporting.

Every quantity in the system shall be associated with one Unit of Measure.

---

# 2. Purpose

The purpose of Unit of Measure is to standardize how business quantities are represented.

Examples:

- Piece
- Set
- Pair
- Meter
- Kilogram
- Gram
- Litre
- Box
- Roll

Rather than allowing arbitrary quantity descriptions, AaramBooks maintains a controlled catalogue of Units of Measure.

---

# 3. Business Responsibilities

The Unit of Measure Business Object is responsible for:

- Maintaining standard business units.
- Providing quantity consistency.
- Supporting inventory management.
- Supporting procurement.
- Supporting reporting.
- Supporting future unit conversions.

The Unit of Measure Business Object is **not** responsible for:

- Inventory calculations.
- Unit conversion calculations.
- Stock valuation.
- Procurement transactions.

---

# 4. Business Importance

**Priority:** Critical

Every Inventory Item requires one Unit of Measure.

Without Unit of Measure:

- Quantities become ambiguous.
- Inventory cannot be managed consistently.
- Procurement becomes unreliable.
- Reports become inaccurate.

---

# 5. Business Rules

### Rule 1

Every Unit of Measure shall have one unique Unit Code.

---

### Rule 2

Every Unit of Measure shall have one unique Unit Name.

---

### Rule 3

A Unit of Measure represents one standardized business unit.

---

### Rule 4

A Unit of Measure cannot be deleted once referenced by an Inventory Item.

Inactive or Archived status should be used instead.

---

### Rule 5

Historical transactions shall preserve the Unit of Measure originally used.

---

### Rule 6

Unit Code is immutable.

---

# 6. Business Relationships

## Parent

Company

---

## Children

None

---

## Referenced By

- Inventory Item
- SKU
- Procurement
- Inventory Intelligence
- Reports

---

# 7. Business Lifecycle

```
Create

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

Historical business records shall always retain their original Unit of Measure.

---

# 8. Business Events

The Unit of Measure Business Object publishes:

- Unit Created
- Unit Updated
- Unit Activated
- Unit Deactivated
- Unit Archived

These events communicate completed business facts.

---

# 9. Business Attributes

| Attribute | Required | Business Type | Editable | Unique | Default |
|------------|----------|---------------|----------|--------|----------|
| Unit Code | Yes | Identifier | No | Yes | None |
| Unit Name | Yes | Name | Yes | Yes | None |
| Short Name | Yes | Name | Yes | Yes | None |
| Description | No | Description | Yes | No | None |
| Status | Yes | Status | System | No | Active |
| Created On | Yes | Audit | No | No | System |
| Created By | Yes | Audit | No | No | System |
| Updated On | Yes | Audit | No | No | System |
| Updated By | Yes | Audit | No | No | System |

---

# 10. Validation Rules

- Unit Code cannot be blank.
- Unit Code must be unique.
- Unit Name cannot be blank.
- Short Name cannot be be blank.
- Status must be one of:
  - Active
  - Inactive
  - Archived
- Audit fields are system maintained.

---

# 11. UI Requirements

The Unit of Measure module shall provide:

- Unit List
- Create Unit
- Edit Unit
- View Unit
- Archive Unit

Users should be able to search and filter Units of Measure.

---

# 12. API Requirements

The Unit of Measure Business Object shall expose APIs for:

- List Units
- Get Unit
- Create Unit
- Update Unit
- Activate Unit
- Deactivate Unit
- Archive Unit

Deletion API shall not be provided.

---

# 13. Database Considerations

The Unit of Measure Business Object shall be stored as a master table.

Business transactions shall reference the Unit rather than duplicating its information.

Future versions should support unit conversion without redesigning the Business Object.

---

# 14. Implementation Notes

The implementation shall:

- Never duplicate Unit definitions.
- Never allow deletion once referenced.
- Preserve historical references.
- Follow the Engineering Constitution.
- Follow the Enterprise Information Model.
- Follow the Enterprise Event Model.

If additional Business Attributes or Business Rules are required, update this specification before changing the implementation.

---

# 15. Future Scope

Future releases may introduce:

- Unit Groups
- Base Units
- Unit Conversion Rules
- Decimal Precision
- Packaging Units
- Purchase Unit vs Stock Unit
- Sales Unit

These enhancements shall extend the Unit of Measure Business Object without changing its core responsibility.

---

# 16. Definition of Done

The Unit of Measure Business Object is complete when:

- Business rules are implemented.
- Business attributes are implemented.
- Validation rules are implemented.
- Business events are published.
- Database schema is implemented.
- APIs are implemented.
- UI is implemented.
- Unit tests pass.
- Documentation is updated.
- Architecture remains compliant with the Enterprise Architecture.

---

# 17. References

This Business Object shall comply with:

- Business Model
- System Architecture
- Event Model
- Information Model
- Masters Domain README
- Engineering Constitution