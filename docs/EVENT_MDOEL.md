# Task: Create `03_EVENT_MODEL.md`

## Objective

Create the Event Model document for the **AaramBooks Platform**.

This document defines how business activities are represented as events throughout the platform.

It explains:

- What an event is.
- Why the platform is event-driven.
- Event ownership.
- Event classification.
- Event processing.
- Inventory Movements.
- Event immutability.
- Event lifecycle.

The Event Model shall become the communication contract between all business domains.

This document must remain independent of programming languages, databases, APIs and implementation details.

---

# Event Philosophy

The AaramBooks Platform follows an Event Driven Architecture.

Every meaningful business activity performed within the platform shall create one or more Business Events.

Business Events become the permanent historical record of business activities.

Inventory, Analytics and future AI capabilities shall derive their information from Business Events.

Business Events represent facts.

They shall not represent user interface actions.

Examples

Correct

- Material Received
- Sale Recorded
- Damage Recorded
- Warehouse Transfer Completed

Incorrect

- Save Button Clicked
- Purchase Screen Opened

---

# Core Principles

Establish the following principles.

---

## Business Events are Immutable

Once a Business Event has been posted it shall never be modified.

Corrections shall be performed through:

- Reversal Events
- Adjustment Events
- Compensating Events

The original event shall always remain part of the business history.

---

## Event Versioning

The platform shall support Event Versioning while preserving Event Immutability.

Business Events shall never be edited or deleted after they have been posted.

When a correction is required, the platform shall create a new Event Version that references the original event.

Every version shall maintain:

- Version Number
- Parent Event Reference
- Reason for Change
- Timestamp
- User
- Change Type

The complete history of all event versions shall always remain available for audit purposes.

Consumers such as the Inventory Engine and Analytics shall always process the latest valid version while preserving historical versions for traceability.

Event Versioning shall ensure:

- Complete audit trail
- Historical accuracy
- Safe corrections
- Regulatory compliance
- Future reconciliation capabilities

## Every Event has One Publisher

Every Business Event shall be published by exactly one business domain.

Examples

Material Received

Publisher

Procurement

Sale Recorded

Publisher

Operations

Supplier Created

Publisher

Reference Data

Inventory Engine never publishes Business Events.

---

## Every Event has Multiple Consumers

A Business Event may be consumed by multiple domains.

Example

Sale Recorded

Consumers

- Inventory Engine
- Analytics
- Dashboard (through Analytics)
- Notifications (Future)

---

## Inventory is Derived

Inventory shall never be edited directly.

Inventory shall always be derived from standardized Inventory Movements generated from Business Events.

---

## Analytics is Derived

Analytics shall never generate business data.

Analytics consumes Business Events and Inventory information to generate business intelligence.

---

# Event Classification

Classify all platform events into the following categories.

---

## Reference Data Events

Examples

- Company Created
- SKU Created
- SKU Updated
- Supplier Created
- Warehouse Created
- Inventory Classification Created
- Attribute Definition Created

---

## Procurement Events

Examples

- Material Received
- Purchase Returned
- Purchase Invoice Received
- Purchase Invoice Updated
- Vendor Payment Recorded

---

## Operations Events

Examples

- Sale Recorded
- Sale Returned
- Job Work Issued
- Job Work Received
- Warehouse Transfer Completed
- Inventory Adjustment Recorded
- Damage Recorded
- Internal Consumption Recorded

---

## Inventory Events

Inventory Engine shall consume standardized Inventory Movements.

Inventory shall not understand Procurement or Operations directly.

Inventory Movements include

- Increase Stock
- Decrease Stock
- Transfer Stock
- Reserve Stock (Future)
- Release Stock (Future)
- Recalculate Stock
- Inventory Adjustment

---

## Analytics Events

Examples

- KPI Updated
- Report Refreshed
- Dashboard Dataset Updated
- Inventory Metrics Updated
- Procurement Metrics Updated

---

## Integration Events

Examples

- ShopDeck Import Completed
- Amazon Import Completed
- Vyapar Export Completed
- Excel Imported
- Synchronization Failed

---

## Administration Events

Examples

- User Created
- Role Assigned
- Permission Updated
- Approval Granted
- Approval Rejected

---

# Event Pipeline

Describe the standard platform event pipeline.

Business Activity

↓

Business Event

↓

Validation

↓

Inventory Movement (if applicable)

↓

Inventory Engine

↓

Analytics

↓

Dashboard

↓

Notification (Future)

Every business process shall follow this pipeline.

---

# Business Event → Inventory Movement Mapping

Create a mapping table.

Examples

Business Event

Material Received

Inventory Movement

Increase Stock

----------------------------

Purchase Return

↓

Decrease Stock

----------------------------

Sale Recorded

↓

Decrease Stock

----------------------------

Sale Return

↓

Increase Stock

----------------------------

Job Work Issue

↓

Transfer Stock

----------------------------

Job Work Receipt

↓

Increase Finished Goods

Decrease Raw Materials (where applicable)

----------------------------

Warehouse Transfer

↓

Transfer Stock

----------------------------

Inventory Adjustment

↓

Increase / Decrease Stock

----------------------------

Damage Recorded

↓

Decrease Stock

---

# Event Structure

Every Business Event shall contain a standard structure.

Include:

Event ID

Event Type

Event Category

Publishing Domain

Business Object

Reference Number

Reference Object

Event Timestamp

Effective Date

Warehouse

SKU

Quantity

Unit of Measure

User

Status

Remarks

Attachments (Future)

Every event across the platform shall follow the same metadata structure.

---

# Event Lifecycle

Define the lifecycle of an event.

Draft

↓

Validated

↓

Posted

↓

Consumed

↓

Archived

Events shall never return to an earlier state.

---

# Event Ownership

Define which domain publishes each Business Event.

Reference Data

↓

Reference Data Events

Procurement

↓

Procurement Events

Operations

↓

Operations Events

Inventory Engine

↓

Inventory Movements

Analytics

↓

Analytical Events

Administration

↓

Administration Events

---

# Event Consumers

Describe who consumes events.

Inventory Engine

Consumes

Inventory Movements

Analytics

Consumes

Business Events
Inventory Information

Dashboard

Consumes

Analytics

Integrations

Consumes

External Platform Events

Future AI

Consumes

Business Events
Inventory
Analytics

---

# Event Processing Rules

Establish platform-wide processing rules.

Examples

- Events shall be processed in chronological order.
- Every event shall have a unique identifier.
- Every event shall be traceable to its source.
- Events shall be auditable.
- Events shall never be silently discarded.
- Failed processing shall be logged.
- Every Inventory Movement shall originate from a Business Event.
- Analytics shall never modify Business Events.
- Inventory Engine shall never modify Business Events.

---

# Event Traceability

Describe complete traceability.

Example

ShopDeck Order

↓

Integration Event

↓

Sale Recorded

↓

Inventory Movement

↓

Inventory Updated

↓

Analytics Updated

↓

Dashboard KPI Updated

Every stage shall be traceable.

---

# Future Expansion

Describe how future domains publish events.

Examples

Manufacturing

Rental

CRM

Vendor Portal

Accounting

Barcode

Mobile App

Every future domain shall publish standardized Business Events without modifying the Event Model.

---

# Out of Scope

Do NOT include

- SQL
- Database Tables
- APIs
- REST
- GraphQL
- Programming Languages
- Frameworks
- UI
- Implementation

---

# Writing Style

Write the document as an Enterprise Event Architecture document.

Maintain technology independence.

Focus entirely on event philosophy, event ownership, event flow and business behaviour.

This document shall become the behavioral contract for the entire AaramBooks Platform.