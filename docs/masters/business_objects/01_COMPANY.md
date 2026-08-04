# Company Business Object

**Domain:** Masters

**Version:** 1.0

**Status:** Approved

---

# 1. Objective

The Company Business Object represents the legal business entity operating within the AaramBooks platform.

It establishes the highest level of ownership for all business information and business operations.

Every Business Object and every Business Transaction ultimately belongs to one Company.

The Company Business Object is the root Master Data object of AaramBooks.

---

# 2. Purpose

The purpose of Company is to provide the legal and organizational identity of the business.

Instead of storing company information throughout the platform, AaramBooks maintains one authoritative Company Business Object that is referenced wherever required.

Company provides ownership for:

- Suppliers
- Warehouses
- Inventory Items
- Procurement
- Inventory Operations
- Reports
- Platform Configuration

---

# 3. Business Responsibilities

The Company Business Object is responsible for:

- Maintaining company identity.
- Maintaining legal business information.
- Maintaining tax registration information.
- Maintaining primary contact information.
- Maintaining company address.
- Providing ownership to all business operations.
- Supporting future multi-company architecture.

The Company Business Object is **not** responsible for:

- Procurement
- Inventory
- Accounting
- Reporting
- Stock Management

---

# 4. Business Importance

**Priority:** Critical

Company is the highest-level Business Object.

Without a Company:

- No Supplier can exist.
- No Warehouse can exist.
- No Inventory Item can exist.
- No Procurement can occur.
- No Reports can be generated.

---

# 5. Business Rules

### Rule 1

Every Company shall have one unique Company Code.

---

### Rule 2

Every Company shall have one official Company Name.

---

### Rule 3

A Company shall have one legal identity.

---

### Rule 4

Every Master Data Business Object belongs to one Company.

---

### Rule 5

Historical transactions shall always retain Company ownership.

---

### Rule 6

A Company shall never be permanently deleted after operational data exists.

Inactive or Archived status should be used instead.

---

### Rule 7

Company Code is immutable.

---

# 6. Business Relationships

## Parent

None

Company is the root Business Object.

---

## Children

- Supplier
- Warehouse
- Inventory Item
- Brand
- Collection
- Category
- Subcategory
- Product Attribute

---

## Referenced By

- Procurement
- Inventory Intelligence
- Reports
- Platform Administration

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

Historical business information shall always remain associated with the Company.

---

# 8. Business Events

The Company Business Object publishes the following Business Events.

- Company Created
- Company Updated
- Company Activated
- Company Deactivated
- Company Archived

Business Events communicate completed business facts.

They never instruct other domains what to do.

---

# 9. Business Attributes

| Attribute | Required | Business Type | Editable | Unique | Default |
|------------|----------|---------------|----------|--------|----------|
| Company Code | Yes | Identifier | No | Yes | None |
| Company Name | Yes | Name | Yes | Yes | None |
| Legal Name | Yes | Name | Yes | No | None |
| Display Name | No | Name | Yes | No | Company Name |
| GSTIN | Yes | Tax Identifier | Yes | Yes | None |
| PAN | Yes | Tax Identifier | Yes | Yes | None |
| Email | No | Contact | Yes | No | None |
| Phone | No | Contact | Yes | No | None |
| Mobile | No | Contact | Yes | No | None |
| Website | No | Contact | Yes | No | None |
| Address Line 1 | Yes | Address | Yes | No | None |
| Address Line 2 | No | Address | Yes | No | None |
| City | Yes | Address | Yes | No | None |
| State | Yes | Address | Yes | No | None |
| Country | Yes | Address | Yes | No | India |
| PIN Code | Yes | Address | Yes | No | None |
| Status | Yes | Status | System | No | Active |
| Created On | Yes | Audit | No | No | System |
| Created By | Yes | Audit | No | No | System |
| Updated On | Yes | Audit | No | No | System |
| Updated By | Yes | Audit | No | No | System |

---

# 10. Validation Rules

- Company Code cannot be blank.
- Company Code must be unique.
- Company Name cannot be blank.
- GSTIN must be valid.
- PAN must be valid.
- Status must be one of:
  - Active
  - Inactive
  - Archived
- Country defaults to India.
- Audit fields are system maintained.

---

# 11. UI Requirements

The Company module shall provide:

- Company Profile
- Edit Company
- Company Settings
- Company Address
- Tax Information

Company creation screen will generally be used only during initial platform setup.

---

# 12. API Requirements

The Company Business Object shall expose APIs for:

- Get Company
- Update Company
- Activate Company
- Deactivate Company

Company creation and deletion APIs are not expected during normal business operations.

---

# 13. Database Considerations

The Company Business Object shall be stored as a single authoritative record.

Future versions should support multiple companies without requiring architectural redesign.

The database implementation shall preserve historical ownership of all business data.

---

# 14. Implementation Notes

The implementation shall follow these principles:

- Never duplicate Company information.
- Never allow direct deletion.
- Preserve historical ownership.
- Follow the Engineering Constitution.
- Follow the Enterprise Information Model.
- Follow the Enterprise Event Model.

If implementation requires additional Business Attributes or Business Rules, update this document first before changing the code.

---

# 15. Future Scope

Future releases may introduce:

- Multiple Companies
- Branches
- Business Units
- Departments
- Multiple GST Registrations
- Multiple Addresses
- Contact Persons
- Regional Offices
- Digital Signatures
- Company Logo
- Letterheads
- Banking Information

These enhancements shall extend the Company Business Object without changing its core responsibility.

---

# 16. Definition of Done

The Company Business Object is considered complete when:

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