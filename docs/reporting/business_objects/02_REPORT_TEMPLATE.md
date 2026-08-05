# Report Template

## Purpose

The Report Template Business Object defines the presentation layer of a Report.

A Report Template controls how business information is rendered without changing the underlying business logic or data retrieval process.

It specifies the visual structure, layout, formatting, grouping, sorting, branding, pagination, and export behavior of a Report.

Multiple Report Templates may be associated with the same Report, allowing different users, departments, or export formats to view identical data in different ways.

A Report Template never modifies business data.

---

# Responsibilities

The Report Template is responsible for:

* Defining report layouts.
* Controlling visible columns.
* Configuring column order.
* Defining grouping behavior.
* Defining sorting behavior.
* Applying formatting rules.
* Supporting branding.
* Supporting export layouts.
* Supporting print layouts.

The Report Template is **not** responsible for:

* Retrieving business data.
* Executing business logic.
* Applying business calculations.
* Managing report permissions.
* Creating reports.

---

# Design Philosophy

Business information and presentation must remain independent.

A Report answers:

> **What information should be displayed?**

A Report Template answers:

> **How should that information be displayed?**

This separation allows a single Report to support multiple layouts without changing the Report definition.

---

# Business Attributes

## Identification

| Attribute     | Description                |
| ------------- | -------------------------- |
| Template Code | Unique business identifier |
| Template Name | Display name               |
| Description   | Business description       |

---

## Report Association

| Attribute        | Description                                    |
| ---------------- | ---------------------------------------------- |
| Report           | Parent Report                                  |
| Default Template | Indicates whether this is the default template |

---

## Layout Configuration

| Attribute   | Description          |
| ----------- | -------------------- |
| Orientation | Portrait / Landscape |
| Page Size   | A4, Letter, etc.     |
| Margins     | Page margins         |
| Header      | Header configuration |
| Footer      | Footer configuration |

---

## Column Configuration

For every column:

| Attribute   | Description         |
| ----------- | ------------------- |
| Column Name | Display label       |
| Field       | Source field        |
| Width       | Display width       |
| Alignment   | Left, Center, Right |
| Visible     | Yes / No            |
| Sortable    | Yes / No            |
| Groupable   | Yes / No            |

---

## Formatting Rules

The template defines formatting for:

* Dates
* Currency
* Quantity
* Percentage
* Decimal Precision
* Negative Values
* Null Values

---

## Branding

Optional branding includes:

* Company Logo
* Company Name
* Address
* Footer Text
* Report Title
* Watermark

---

## Export Configuration

Defines export behavior for:

* Excel
* CSV
* PDF

Each export format may have different formatting rules.

---

## Status

| Attribute | Description       |
| --------- | ----------------- |
| Status    | Active / Inactive |

---

# Validation Rules

* Template Code must be unique.
* Template Name must be unique.
* Report is mandatory.
* At least one visible column is required.
* Status is mandatory.

---

# Business Rules

## Rule 1

A Report Template never changes business data.

---

## Rule 2

Multiple Templates may exist for the same Report.

Example:

Sales Report

↓

Executive Template

↓

Operations Template

↓

Detailed Audit Template

---

## Rule 3

Exactly one Template may be designated as the default for a Report.

---

## Rule 4

Column visibility affects presentation only.

Hidden columns remain available to the Report Engine if required for calculations or grouping.

---

## Rule 5

Templates may define default sorting and grouping.

Users may override these settings unless restricted by permissions.

---

## Rule 6

Inactive Templates cannot be selected for new report generation.

Historical reports remain unaffected.

---

## Rule 7

Deleting Templates is prohibited.

Templates may only be marked as Inactive.

---

# Relationships

The Report Template relates to:

* Report
* Report Filter
* Dashboard
* Report Export

---

# Lifecycle

```text
ACTIVE

↓

INACTIVE
```

Templates remain available for audit purposes after becoming inactive.

---

# Rendering Workflow

```text
Report Data

↓

Apply Template

↓

Apply Column Rules

↓

Apply Formatting

↓

Apply Branding

↓

Render Output

↓

Display / Print / Export
```

---

# Performance Requirements

Report Templates should:

* Render efficiently.
* Support large reports.
* Minimize formatting overhead.
* Support reusable layouts.
* Avoid unnecessary recalculations.

---

# Security

Templates inherit Report permissions.

Only authorized users may:

* Create Templates.
* Modify Templates.
* Set Default Templates.
* Activate or Inactivate Templates.

---

# API Design

Typical endpoints include:

```text
GET    /report-templates
GET    /report-templates/{id}
POST   /report-templates
PUT    /report-templates/{id}
PATCH  /report-templates/{id}/activate
PATCH  /report-templates/{id}/deactivate
```

---

# Events

Templates may publish:

* ReportTemplateCreated
* ReportTemplateUpdated
* ReportTemplateActivated
* ReportTemplateDeactivated

---

# Reporting Impact

Report Templates determine:

* Layout
* Readability
* Printability
* Branding
* Export appearance
* User experience

They do not influence business calculations or report results.

---

# Examples

## Executive Template

Characteristics:

* Summary totals
* Charts
* KPIs
* Minimal detail

---

## Operations Template

Characteristics:

* Detailed rows
* Warehouse information
* SKU information
* Order status

---

## Audit Template

Characteristics:

* Every business field
* Technical identifiers
* Timestamps
* User information

---

# Edge Cases

The Report Template must gracefully handle:

* Hidden mandatory columns.
* Empty reports.
* Large numbers of columns.
* Dynamic column widths.
* Export format differences.
* Long text fields.
* Missing branding assets.

---

# Future Enhancements

Future versions may support:

* Drag-and-drop template designer.
* User-specific templates.
* Company-specific branding.
* Conditional formatting.
* Dynamic column visibility.
* Theme support.
* Responsive layouts.

---

# Guiding Principle

**A Report Template defines presentation, not information.**

It allows the same business data to be viewed in multiple ways while ensuring that presentation remains completely independent of business logic and data retrieval.
