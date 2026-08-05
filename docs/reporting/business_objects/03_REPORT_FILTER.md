# Report Filter

## Purpose

The Report Filter Business Object defines reusable criteria used to limit, refine, and organize the data returned by a Report.

Rather than embedding filtering logic inside every Report, the Reporting Engine uses Report Filters as independent business objects that can be reused across multiple reports, dashboards, scheduled reports, and exports.

Report Filters improve report usability, maintain consistency across the platform, and optimize report execution performance.

A Report Filter never modifies business data.

It only controls which business data is included in a report.

---

# Responsibilities

The Report Filter is responsible for:

* Defining reusable filtering criteria.
* Restricting report datasets.
* Supporting parameterized reports.
* Improving report performance.
* Providing consistent filtering across reports.
* Supporting user-specific filter preferences.
* Supporting saved filter configurations.

The Report Filter is **not** responsible for:

* Retrieving business data.
* Performing business calculations.
* Defining report layouts.
* Managing report permissions.
* Exporting reports.

---

# Design Philosophy

Every report answers a business question.

Every Report Filter narrows that question.

Example:

Without Filter

> Show all Sales Orders.

With Filter

> Show completed Amazon Sales Orders from April 2026 belonging to Warehouse Delhi.

The Report remains identical.

Only the Filter changes.

---

# Business Attributes

## Identification

| Attribute   | Description                |
| ----------- | -------------------------- |
| Filter Code | Unique business identifier |
| Filter Name | Display name               |
| Description | Business description       |

---

## Report Association

| Attribute      | Description                            |
| -------------- | -------------------------------------- |
| Report         | Associated Report                      |
| Default Filter | Indicates default filter configuration |

---

## Filter Criteria

A Report Filter may contain one or more filter conditions.

Examples include:

* Company
* Warehouse
* Channel
* Customer
* SKU
* Category
* Inventory Item
* Sales Order Status
* Payment Status
* Settlement Status
* Import Job Status
* Financial Period

---

## Date Filters

Supported date filters include:

* Today
* Yesterday
* This Week
* Last Week
* This Month
* Last Month
* This Financial Year
* Custom Date Range

---

## Numeric Filters

Supported comparisons:

* Equals
* Not Equals
* Greater Than
* Less Than
* Between

Examples:

* Revenue
* Quantity
* Inventory Value
* GST Amount
* Payment Amount

---

## Text Filters

Supported operations:

* Equals
* Contains
* Starts With
* Ends With

Examples:

* SKU Code
* Customer Name
* Invoice Number
* Settlement ID

---

## Status Filters

Examples:

* Active
* Inactive
* Draft
* Approved
* Posted
* Archived

---

## Sorting

Each Report Filter may define:

* Primary Sort
* Secondary Sort
* Ascending
* Descending

---

## Grouping

Examples:

* Company
* Warehouse
* Category
* SKU
* Customer
* Sales Channel
* Financial Period

---

## Status

| Attribute | Description       |
| --------- | ----------------- |
| Status    | Active / Inactive |

---

# Validation Rules

* Filter Code must be unique.
* Filter Name must be unique.
* Report is mandatory.
* At least one filtering criterion is required.
* Status is mandatory.

---

# Business Rules

## Rule 1

A Report Filter never changes business data.

---

## Rule 2

Multiple Filters may exist for the same Report.

Example:

Sales Report

↓

Today's Sales

↓

Monthly Sales

↓

Amazon Sales

↓

Warehouse Sales

---

## Rule 3

Exactly one Filter may be designated as the default for a Report.

---

## Rule 4

Filter criteria are evaluated using logical operators.

Supported operators include:

* AND
* OR

Nested conditions may be supported in future versions.

---

## Rule 5

Filters must be deterministic.

The same filter applied to the same dataset must always return identical results.

---

## Rule 6

Inactive Filters cannot be selected for new report generation.

Historical reports remain unaffected.

---

## Rule 7

Deleting Filters is prohibited.

Filters may only be marked as Inactive.

---

# Relationships

The Report Filter relates to:

* Report
* Report Template
* Dashboard
* Widget
* Scheduled Report

---

# Lifecycle

```text id="khp4zx"
ACTIVE

↓

INACTIVE
```

---

# Filtering Workflow

```text id="fr8ybn"
User Request

↓

Select Report

↓

Select Filter

↓

Validate Filter

↓

Retrieve Matching Data

↓

Generate Report
```

---

# Performance Requirements

The Report Filter should:

* Support indexed database fields.
* Avoid unnecessary full-table scans.
* Enable efficient pagination.
* Support millions of business records.
* Minimize query execution time.

Future implementations may include query optimization and caching.

---

# Security

Filters inherit Report permissions.

Users may only apply filters to data they are authorized to access.

Security restrictions such as Company, Warehouse, and Financial Period isolation must always be enforced before user-defined filters.

---

# API Design

Typical endpoints include:

```text id="apv6st"
GET    /report-filters
GET    /report-filters/{id}
POST   /report-filters
PUT    /report-filters/{id}
PATCH  /report-filters/{id}/activate
PATCH  /report-filters/{id}/deactivate
```

---

# Events

Report Filters may publish:

* ReportFilterCreated
* ReportFilterUpdated
* ReportFilterActivated
* ReportFilterDeactivated

---

# Reporting Impact

Report Filters influence:

* Report contents
* Dashboard metrics
* Scheduled Reports
* Exported reports
* Business analytics

They never alter the underlying business data.

---

# Examples

## Sales Report Filter

Criteria:

* Date Range = Current Month
* Channel = Website
* Status = Completed

Returns only completed website orders for the current month.

---

## Inventory Report Filter

Criteria:

* Warehouse = Delhi
* Category = Bedding
* Quantity Available < 20

Returns low-stock bedding items in the Delhi warehouse.

---

## Financial Report Filter

Criteria:

* Financial Period = FY2026-27
* Ledger Type = Expense

Returns only expense ledger activity for the selected financial year.

---

# Edge Cases

The Report Filter must gracefully handle:

* Empty result sets.
* Invalid filter combinations.
* Large date ranges.
* Archived business objects.
* Deleted master references.
* Missing optional filter values.

---

# Future Enhancements

Future versions may support:

* Nested filter groups.
* User-saved personal filters.
* Shared team filters.
* Dynamic filter suggestions.
* AI-generated filters.
* Visual query builder.
* Geographic filters.
* Full-text search.

---

# Guiding Principle

**A Report Filter defines *which* business information is presented, never *how* it is calculated.**

By separating filtering from reporting logic, AaramBooks ensures that reports remain reusable, deterministic, secure, and scalable while giving users the flexibility to analyze business data from multiple perspectives without duplicating report definitions.
