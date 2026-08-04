# README – Create `04_INFORMATION_MODEL.md` (Part 2)

# Business Object Catalogue

## Objective

The Business Object Catalogue shall become the master index of all Business Objects within the AaramBooks Platform.

It serves as the official business vocabulary of the platform.

Every Business Object that exists within the business shall appear exactly once in this catalogue.

The catalogue is intended to answer the following questions:

- What Business Objects exist?
- Which business domain owns each Business Object?
- What category does each Business Object belong to?
- Is the Business Object operational, analytical or derived?
- Does the Business Object represent reference information or business activity?

The catalogue is not intended to explain individual Business Objects in detail.

Its purpose is identification and classification.

Detailed definitions will be documented later using the Business Object Template.

---

# Catalogue Design Principles

Establish the following principles.

## Complete Coverage

Every significant business concept within AaramBooks shall appear in the Business Object Catalogue.

The catalogue shall become the authoritative inventory of Business Objects.

---

## Single Representation

Every Business Object shall appear exactly once.

The same Business Object shall never appear under multiple categories.

---

## Business Terminology

Business Objects shall always use business language.

Avoid technical terminology.

Do not use:

- Tables
- Models
- DTOs
- APIs
- JSON Objects
- Database terminology

The catalogue represents the business, not the implementation.

---

## Stable Classification

Business Objects shall remain in their assigned category.

Categories should not change because of implementation choices.

---

# Catalogue Organization

Organize the catalogue using the Business Object Classification established in Part 1.

Each category shall contain its Business Objects together with a brief one-line description.

Do not provide detailed specifications yet.

---

# Reference Business Objects

Describe the purpose of Reference Business Objects.

Then create a catalogue similar to the following.

| Business Object | Purpose |
|-----------------|---------|
| Company | Represents the legal business operating the platform. |
| Inventory Classification | Defines the hierarchical categorization of inventory. |
| Inventory Item | Represents a generic inventory product family. |
| SKU | Represents a uniquely sellable or stockable inventory unit. |
| Supplier | Represents organizations supplying materials or finished goods. |
| Job Worker | Represents external parties performing manufacturing or processing work. |
| Warehouse | Represents physical or logical inventory storage locations. |
| Brand | Represents commercial branding of inventory items. |
| Collection | Represents marketing or product collections. |
| Unit of Measure | Defines standardized inventory measurement units. |
| Attribute Definition | Defines reusable inventory attributes used across products. |

After the catalogue, explain the role of Reference Business Objects within the platform.

Discuss why every operational process depends upon Reference Business Objects.

---

# Transactional Business Objects

Explain the purpose of Transactional Business Objects.

Create a catalogue.

| Business Object | Purpose |
|-----------------|---------|
| Material Receipt | Records receipt of physical inventory. |
| Purchase Return | Records return of purchased inventory. |
| Purchase Invoice | Represents commercial purchase documentation. |
| Vendor Payment | Represents settlement of supplier obligations. |
| Sale | Records inventory leaving the business through sales. |
| Sale Return | Records inventory returned by customers. |
| Job Work Issue | Records inventory issued to job workers. |
| Job Work Receipt | Records inventory received back from job workers. |
| Warehouse Transfer | Records inventory movement between warehouses. |
| Inventory Adjustment | Records approved stock corrections. |
| Damage | Records damaged inventory. |
| Internal Consumption | Records inventory consumed internally. |
| Stock Verification | Records physical verification of inventory. |

Discuss the role of transactional information.

Explain that these Business Objects represent actual business activity.

---

# Derived Business Objects

Explain that Derived Business Objects are calculated by the platform.

Create a catalogue.

| Business Object | Purpose |
|-----------------|---------|
| Current Stock | Current physical inventory position. |
| Stock Ledger | Chronological history of inventory movements. |
| Stock Availability | Inventory available for allocation. |
| Inventory Valuation | Calculated financial value of inventory. |
| Inventory Snapshot | Point-in-time inventory summary. |

Discuss why Derived Business Objects are never manually maintained.

---

# Analytical Business Objects

Explain the purpose of analytical information.

Create a catalogue.

| Business Object | Purpose |
|-----------------|---------|
| Report | Structured presentation of business information. |
| KPI | Business performance indicator. |
| Dashboard Dataset | Data prepared for dashboard visualization. |
| Trend | Time-based analytical information. |
| Forecast | Predicted future business information. |
| Supplier Performance | Supplier analytical evaluation. |
| Inventory Performance | Inventory analytical evaluation. |
| Purchase Analysis | Procurement performance analysis. |
| Sales Analysis | Sales performance analysis. |
| ABC Classification | Inventory classification based on business importance. |

Discuss how Analytical Business Objects differ from Derived Business Objects.

---

# Platform Business Objects

Explain their purpose.

Create a catalogue.

| Business Object | Purpose |
|-----------------|---------|
| User | Represents a platform user. |
| Role | Defines security roles. |
| Permission | Defines platform permissions. |
| Audit Log | Records platform audit information. |
| Import Job | Represents external data import operations. |
| Export Job | Represents external data export operations. |
| Notification | Represents system notifications. |
| Approval Workflow | Represents configurable approval processes. |

Discuss why Platform Business Objects are separated from operational business information.

---

# Business Object Template

## Objective

Every Business Object documented within AaramBooks shall follow a single standardized documentation template.

The objective of the template is to ensure:

- Consistency
- Completeness
- Standard terminology
- Easier maintenance
- Future scalability

Every Business Object Specification shall use this template without exception.

---

# Standard Business Object Template

Each Business Object Specification shall include the following sections.

---

## Business Object Name

Provide the official business name.

Business names shall remain stable.

---

## Purpose

Explain why the Business Object exists.

Focus on business value.

---

## Business Description

Describe the Business Object using business language.

Avoid implementation terminology.

---

## Business Category

Specify one of the following.

- Reference
- Transactional
- Derived
- Analytical
- Platform

Explain why the object belongs to this category.

---

## Authoritative Owner

Identify the business domain responsible for the Business Object.

Explain ownership responsibilities.

---

## Consumers

List business domains that consume the Business Object.

Explain why they consume it.

---

## Business Rules

Reference the Business Rules governing the object.

Do not redefine the rules here.

Simply reference them.

---

## Lifecycle Pattern

Reference the appropriate lifecycle pattern defined in the Business Object Lifecycle Model.

Explain why the selected lifecycle applies.

---

## Future Expansion

Discuss how the Business Object may evolve.

Examples:

- Additional workflows
- Integration with future domains
- Additional capabilities
- AI support

---

# Business Object Documentation Principles

Explain the following principles.

Business Objects describe the business.

Business Objects shall remain implementation independent.

Business Objects shall never define Business Attributes.

Business Attributes belong exclusively to the Data Dictionary.

Business Relationships belong to the Business Relationship Model.

Business Rules belong to the Business Rules Model.

Business Object Specifications shall focus only on the Business Object itself.

Conclude Part 2 by explaining that the Business Object Catalogue establishes the vocabulary of AaramBooks, while the Business Object Template establishes the standard by which every Business Object will be documented.

The next part of the Information Model will define the Business Relationship Model and the Business Rules Model.