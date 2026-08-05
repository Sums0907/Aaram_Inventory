# Scheduled Report

## Purpose

The Scheduled Report Business Object represents an automated reporting configuration that generates and distributes Reports according to predefined schedules.

Scheduled Reports eliminate manual report generation by executing Reports automatically at specified times, applying predefined filters and templates, and delivering the output to designated recipients.

A Scheduled Report acts as the automation layer of the Reporting Engine.

It is responsible for **when** a report is generated—not **how** the report is calculated.

Scheduled Reports never modify business data.

---

# Responsibilities

The Scheduled Report is responsible for:

* Automating report generation.
* Executing reports according to schedules.
* Applying predefined templates.
* Applying predefined filters.
* Distributing generated reports.
* Maintaining execution history.
* Handling scheduling failures.
* Supporting recurring business reporting.

The Scheduled Report is **not** responsible for:

* Creating Reports.
* Defining Report Templates.
* Managing business calculations.
* Updating operational data.
* Sending business notifications unrelated to reporting.

---

# Design Philosophy

Business reporting should not depend on manual effort.

Organizations require recurring information such as:

* Daily Sales
* Weekly Inventory
* Monthly GST
* Quarterly Financial Statements

Scheduled Reports ensure this information is generated consistently and delivered automatically.

---

# Business Attributes

## Identification

| Attribute     | Description                |
| ------------- | -------------------------- |
| Schedule Code | Unique business identifier |
| Schedule Name | Display name               |
| Description   | Business description       |

---

## Report Configuration

| Attribute       | Description        |
| --------------- | ------------------ |
| Report          | Source Report      |
| Report Template | Output layout      |
| Report Filter   | Default filter set |

---

## Schedule Configuration

| Attribute      | Description                                       |
| -------------- | ------------------------------------------------- |
| Frequency      | Hourly, Daily, Weekly, Monthly, Quarterly, Yearly |
| Execution Time | Time of execution                                 |
| Time Zone      | Execution time zone                               |
| Start Date     | First execution date                              |
| End Date       | Optional end date                                 |

---

## Distribution

Supported delivery methods:

* Email
* Download Center
* Internal Notification

Future versions:

* Google Drive
* OneDrive
* SharePoint
* Slack
* Microsoft Teams

---

## Output Configuration

Supported formats:

* Excel
* CSV
* PDF

---

## Execution History

Each execution records:

* Execution Timestamp
* Duration
* Status
* Generated File
* Error Details (if any)

---

## Status

| Attribute | Description       |
| --------- | ----------------- |
| Status    | Active / Inactive |

---

# Schedule Types

## Hourly

Example:

Inventory Alerts every hour.

---

## Daily

Example:

Daily Sales Report at 9:00 PM.

---

## Weekly

Example:

Warehouse Inventory every Monday.

---

## Monthly

Example:

Monthly Profit & Loss.

---

## Quarterly

Example:

Quarterly Business Performance.

---

## Yearly

Example:

Annual Financial Statements.

---

# Validation Rules

* Schedule Code must be unique.
* Schedule Name must be unique.
* Report is mandatory.
* Report Template is mandatory.
* Frequency is mandatory.
* Execution Time is mandatory.
* At least one delivery destination is required.
* Status is mandatory.

---

# Business Rules

## Rule 1

A Scheduled Report must reference exactly one Report.

---

## Rule 2

A Scheduled Report may use exactly one Report Template.

---

## Rule 3

A Scheduled Report may use one or more Report Filters.

---

## Rule 4

Only Active Scheduled Reports may execute automatically.

---

## Rule 5

Each execution must create a new report instance.

Previous executions must remain available for audit purposes.

---

## Rule 6

Execution failures must never stop future scheduled executions.

Failures should be logged independently.

---

## Rule 7

Deleting Scheduled Reports is prohibited.

They may only be marked as Inactive.

---

# Relationships

The Scheduled Report relates to:

* Report
* Report Template
* Report Filter
* Report Export
* Dashboard

---

# Lifecycle

```text
ACTIVE

↓

PAUSED

↓

ACTIVE

↓

INACTIVE
```

Paused schedules retain their configuration but do not execute.

Inactive schedules are permanently disabled.

---

# Execution Workflow

```text
Scheduler

↓

Validate Schedule

↓

Load Report

↓

Apply Filters

↓

Apply Template

↓

Generate Report

↓

Export File

↓

Deliver Report

↓

Log Execution
```

---

# Performance Requirements

The Scheduling Engine should:

* Execute reports reliably.
* Support concurrent report generation.
* Queue long-running reports.
* Retry transient failures.
* Maintain execution history.
* Scale to thousands of scheduled reports.

---

# Security

Scheduled Reports inherit permissions from the underlying Report.

Only authorized users may:

* Create schedules.
* Modify schedules.
* Pause schedules.
* Resume schedules.
* View execution history.

Generated reports must only be delivered to authorized recipients.

---

# API Design

Typical endpoints include:

```text
GET    /scheduled-reports
GET    /scheduled-reports/{id}
POST   /scheduled-reports
PUT    /scheduled-reports/{id}
PATCH  /scheduled-reports/{id}/pause
PATCH  /scheduled-reports/{id}/resume
PATCH  /scheduled-reports/{id}/activate
PATCH  /scheduled-reports/{id}/deactivate
GET    /scheduled-reports/{id}/history
```

---

# Events

Scheduled Reports may publish:

* ScheduledReportCreated
* ScheduledReportExecuted
* ScheduledReportSucceeded
* ScheduledReportFailed
* ScheduledReportPaused
* ScheduledReportResumed

Scheduled Reports may consume:

* SchedulerTriggered
* ManualExecutionRequested

---

# Reporting Impact

Scheduled Reports enable:

* Automated operational reporting.
* Automated inventory reporting.
* Automated financial reporting.
* Compliance reporting.
* Executive reporting.
* KPI distribution.

They ensure that business stakeholders receive timely information without manual effort.

---

# Examples

## Daily Sales Report

Frequency:

Daily

Execution Time:

21:00

Template:

Executive Sales Template

Format:

Excel

Recipients:

Sales Manager

Finance Manager

---

## Monthly GST Report

Frequency:

Monthly

Execution Time:

1st day of each month

Format:

PDF

Recipients:

Finance Department

---

## Weekly Inventory Report

Frequency:

Every Monday

Format:

Excel

Recipients:

Warehouse Manager

---

# Edge Cases

The Scheduling Engine must gracefully handle:

* Report execution failures.
* Missing templates.
* Missing recipients.
* Long-running reports.
* Daylight Saving Time adjustments.
* Server restarts.
* Duplicate scheduler triggers.

---

# Future Enhancements

Future versions may support:

* Cron-based scheduling.
* Event-triggered reports.
* Conditional scheduling.
* Approval workflows.
* Multi-company scheduling.
* AI-optimized execution windows.
* Intelligent retry strategies.
* Cloud storage destinations.

---

# Guiding Principle

**Scheduled Reports ensure that critical business information reaches the right people at the right time without manual intervention.**

By separating scheduling from report generation, AaramBooks provides a reliable, scalable, and auditable automation layer that delivers consistent operational, inventory, and financial insights while preserving the integrity of the underlying Reporting Engine.
