# Widget

## Purpose

The Widget Business Object represents a reusable visualization component that displays a specific business metric, KPI, chart, alert, or summary within a Dashboard.

Widgets provide concise, actionable information that enables users to quickly assess business performance without navigating full reports.

A Widget consumes canonical business data through Reports and presents it in a simplified, visual format.

Widgets are read-only business objects.

They never create, modify, or delete business data.

---

# Responsibilities

The Widget is responsible for:

* Displaying KPIs.
* Displaying charts.
* Displaying summarized metrics.
* Displaying alerts.
* Providing drill-down navigation.
* Supporting dashboard composition.
* Supporting real-time monitoring.

The Widget is **not** responsible for:

* Retrieving raw business data directly.
* Performing business calculations.
* Executing workflows.
* Posting accounting transactions.
* Updating inventory.
* Managing reports.

---

# Design Philosophy

A Widget answers a single business question.

Examples include:

* How many orders were received today?
* What is today's revenue?
* Which products are low in stock?
* How much GST is payable?
* Which imports failed?
* Which settlements remain unmatched?

Widgets provide focused answers.

Complex analysis belongs to Reports.

---

# Business Attributes

## Identification

| Attribute   | Description                |
| ----------- | -------------------------- |
| Widget Code | Unique business identifier |
| Widget Name | Display name               |
| Description | Business description       |

---

## Classification

| Attribute     | Description                               |
| ------------- | ----------------------------------------- |
| Widget Type   | KPI, Chart, Table, Alert, Progress        |
| Category      | Operations, Inventory, Finance, Executive |
| Source Report | Associated Report                         |

---

## Visualization

Supported visualization types include:

* Number Card
* Line Chart
* Bar Chart
* Pie Chart
* Donut Chart
* Gauge
* Table
* Progress Indicator
* Alert Banner

---

## Refresh Configuration

| Attribute        | Description             |
| ---------------- | ----------------------- |
| Refresh Mode     | Manual / Automatic      |
| Refresh Interval | Time between updates    |
| Cache Duration   | Optional caching period |

---

## Display Configuration

| Attribute | Description        |
| --------- | ------------------ |
| Width     | Grid width         |
| Height    | Grid height        |
| Position  | Dashboard position |
| Theme     | Visual theme       |

---

## Status

| Attribute | Description       |
| --------- | ----------------- |
| Status    | Active / Inactive |

---

# Widget Categories

## KPI Widget

Displays a single business metric.

Examples:

* Today's Sales
* Orders Today
* Inventory Value
* Outstanding Receivables

---

## Chart Widget

Displays trends and comparisons.

Examples:

* Daily Sales Trend
* Revenue by Channel
* Inventory by Warehouse
* Monthly Profit

---

## Table Widget

Displays summarized business records.

Examples:

* Recent Orders
* Pending Settlements
* Low Stock Items

---

## Alert Widget

Displays important business exceptions.

Examples:

* Negative Inventory
* Failed Imports
* Matching Exceptions
* Overdue Payments

---

## Progress Widget

Displays progress toward business targets.

Examples:

* Monthly Revenue Target
* Inventory Turnover
* Order Fulfillment Rate

---

# Validation Rules

* Widget Code must be unique.
* Widget Name must be unique.
* Widget Type is mandatory.
* Source Report is mandatory.
* Status is mandatory.

---

# Business Rules

## Rule 1

Widgets are read-only.

---

## Rule 2

Every Widget must be associated with exactly one Report.

---

## Rule 3

Widgets must retrieve business information only through the Reporting Engine.

They must never access business domains directly.

---

## Rule 4

Widgets should display summarized information.

Detailed analysis belongs to Reports.

---

## Rule 5

Widgets should support drill-down navigation where appropriate.

Example:

Today's Sales

↓

Click Widget

↓

Open Sales Report

---

## Rule 6

Only Active Widgets may be displayed.

---

## Rule 7

Deleting Widgets is prohibited.

Widgets may only be marked as Inactive.

---

# Relationships

The Widget relates to:

* Dashboard
* Report
* Report Template
* Report Filter

Widgets consume data originating from:

* Operations
* Matching
* Inventory
* Accounting
* Data Ingestion

---

# Lifecycle

```text
ACTIVE

↓

INACTIVE
```

---

# Widget Rendering Workflow

```text
Dashboard Loaded

↓

Load Widget

↓

Execute Report

↓

Apply Filters

↓

Summarize Results

↓

Render Visualization

↓

Display Widget
```

---

# Performance Requirements

Widgets should:

* Load independently.
* Support asynchronous rendering.
* Minimize report execution time.
* Cache frequently requested metrics.
* Avoid blocking dashboard rendering.

A slow Widget should not prevent the remaining Dashboard from loading.

---

# Security

Widgets inherit security from:

* Dashboard
* Report
* Report permissions

Users must never see information they are not authorized to access.

Security restrictions such as Company, Warehouse, Financial Period, and Role must always be enforced before data is displayed.

---

# API Design

Typical endpoints include:

```text
GET    /widgets
GET    /widgets/{id}
GET    /widgets/{id}/render
PATCH  /widgets/{id}/activate
PATCH  /widgets/{id}/deactivate
```

---

# Events

Widgets may publish:

* WidgetRendered
* WidgetRefreshed
* WidgetDrillDownOpened

Widgets may consume:

* DashboardLoaded
* ImportCompleted
* MatchingCompleted
* InventoryUpdated
* JournalPosted

to refresh displayed information automatically.

---

# Reporting Impact

Widgets contribute to:

* Executive Dashboards
* Operations Dashboards
* Inventory Dashboards
* Finance Dashboards
* Business Intelligence

They provide rapid visibility into business performance without replacing detailed Reports.

---

# Examples

## KPI Widget

Displays:

* Today's Revenue

Value:

₹2,35,480

---

## Chart Widget

Displays:

Monthly Revenue Trend

Visualization:

Line Chart

---

## Alert Widget

Displays:

Negative Inventory

Items:

* SKU-101
* SKU-245

---

## Table Widget

Displays:

Latest Orders

Columns:

* Order Number
* Customer
* Amount
* Status

---

# Edge Cases

The Widget must gracefully handle:

* Empty datasets.
* Missing reports.
* Slow report execution.
* Large datasets.
* Permission changes.
* Archived reports.
* Failed refresh attempts.

---

# Future Enhancements

Future versions may support:

* Interactive charts.
* AI-generated insights.
* Predictive KPIs.
* User-customizable widgets.
* Drag-and-drop configuration.
* Real-time push updates.
* Embedded maps.
* Advanced visual analytics.

---

# Guiding Principle

**A Widget presents one business insight, clearly and immediately.**

By encapsulating a single KPI, chart, alert, or summary, Widgets provide reusable building blocks for Dashboards while relying entirely on the Reporting Engine and canonical business data. They enable users to monitor business health at a glance without duplicating business logic or bypassing reporting standards.
