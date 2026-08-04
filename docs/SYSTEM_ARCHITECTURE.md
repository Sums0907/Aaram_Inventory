# Task: Create `02_SYSTEM_ARCHITECTURE.md`

## Objective

Create the System Architecture document for the **AaramBooks Platform**.

This document defines the logical architecture of the platform.

It explains how the platform is organised, how business domains interact, how responsibilities are distributed, and how the architecture supports long-term scalability.

This is an architecture document.

It must not contain implementation details, programming languages, frameworks, database schemas, APIs or UI design.

The document should be written as an Enterprise Software Architecture document.

---

# Overall Goal

The architecture should support the long-term vision of AaramBooks becoming an **Inventory, Operations & Business Intelligence Platform**, while allowing the first implementation phase to focus only on Inventory Management.

The architecture must remain stable even as new business capabilities are added.

---

# Design Principles

The document shall establish the following architectural principles.

## Business Domain Driven Design

Organize the platform around business domains rather than technical layers.

Business domains represent major business capabilities.

Examples include:

- Reference Data
- Procurement
- Operations
- Inventory Engine
- Analytics & Reporting
- Integrations

---

## Single Responsibility Principle

Each business domain shall own one clearly defined responsibility.

Responsibilities shall never overlap.

---

## Single Authoritative Owner

Every business object shall have exactly one Authoritative Owner.

Only the owning domain may create, modify or validate that object.

Other domains may consume the object but shall never own it.

---

## Loose Coupling

Business domains shall communicate through clearly defined contracts.

Domains shall not directly manipulate each other's internal data.

---

## Event Driven Architecture

Business domains publish business events.

Inventory Engine consumes standardized Inventory Movements.

Analytics consumes business data.

Dashboard consumes analytics.

---

## Data First Philosophy

Every business activity shall generate structured business data.

Reports, dashboards, KPIs and future AI capabilities shall always be generated from structured business data.

---

## Scalability

The architecture shall support future business capabilities without requiring redesign of existing domains.

---

# Section 1 – Platform Overview

Describe:

- Purpose of the platform
- Long-term vision
- Phase 1 implementation scope
- Future growth strategy

---

# Section 2 – High Level Architecture

Describe the overall platform architecture.

The platform shall contain the following business domains.

- Reference Data
- Procurement
- Operations
- Inventory Engine
- Analytics & Reporting
- Integrations
- Dashboard
- Administration

Provide a high-level architecture diagram showing relationships between domains.

---

# Section 3 – Business Domains

Create a dedicated subsection for each business domain.

Each subsection should contain:

- Purpose
- Responsibilities
- Business Objects
- Inputs
- Outputs
- Future Expansion

---

## Reference Data

Purpose

Maintain all reusable business reference information.

Business Objects

- Company
- Inventory Classification
- Inventory Items
- SKU
- Attribute Definitions
- Warehouse
- Supplier
- Job Worker
- Unit of Measure
- Brand
- Collection

Reference Data never stores business transactions.

---

## Procurement

Purpose

Manage procurement of inventory.

Responsibilities

- Material Receipt
- Purchase Return
- Purchase Documents
- Purchase History
- Pending Purchase Invoices
- Vendor Payment Tracking

Future

- Purchase Orders
- Vendor Quotations
- Approval Workflow

Only Material Receipt shall affect inventory.

---

## Operations

Purpose

Manage operational business activities.

Responsibilities

- Sales
- Sales Returns
- Job Work Issue
- Job Work Receipt
- Warehouse Transfer
- Damage
- Inventory Adjustment
- Internal Consumption

Operations create business events.

Operations never calculate stock.

---

## Inventory Engine

Purpose

Calculate inventory.

Responsibilities

- Current Stock
- Stock Ledger
- Available Stock
- Inventory Valuation (Future)

Inventory shall never be edited directly.

Inventory shall always be derived from Inventory Movements.

---

## Analytics & Reporting

Purpose

Convert business data into business intelligence.

Include:

Inventory Analytics

Procurement Analytics

Operations Analytics

Cross-Domain Analytics

Future AI Analytics

Analytics never modifies business data.

---

## Integrations

Purpose

Communicate with external systems.

Examples

- ShopDeck
- Amazon
- Vyapar
- Excel
- CSV

Integrations create business events.

They never update inventory directly.

---

## Dashboard

Purpose

Provide business overview.

Dashboard consumes Analytics only.

Dashboard contains no business logic.

---

## Administration

Purpose

Manage platform administration.

Examples

- Users
- Roles
- Permissions
- Audit Logs
- Approval Rules
- Notifications (Future)

Administration does not own business data.

---

# Section 4 – Domain Dependency Matrix

Create the complete Domain Dependency Matrix.

Explain:

- Which domains depend on others.
- Why those dependencies exist.
- Why circular dependencies are prohibited.

Use the following dependency model.

Reference Data

↓

Procurement

↓

Operations

↓

Inventory Engine

↓

Analytics & Reporting

↓

Dashboard

Integrations communicate with Procurement and Operations.

Administration remains independent.

Explain that Inventory Engine depends on standardized Inventory Movements rather than business implementations.

---

# Section 5 – Domain Ownership Matrix

Create a complete Authoritative Ownership Matrix.

Each business object must have:

- Authoritative Owner
- Consumers

Include all major business objects.

Examples:

SKU

Supplier

Warehouse

Purchase

Sales

Job Work

Inventory Adjustment

Current Stock

Stock Ledger

Reports

KPIs

Users

Roles

Audit Logs

Explain the distinction between:

Authoritative Owner

and

Consumer.

---

# Section 6 – Business Process Model

Describe the major business workflows.

Include:

Procurement Workflow

Sales Workflow

Job Work Workflow

Inventory Adjustment Workflow

Each workflow should contain:

- Starting Point
- Major Stages
- Inventory Impact
- Outputs

Business workflows describe business processes.

They are independent of implementation.

---

# Section 7 – High Level Information Flow

Describe how information moves across the platform.

Illustrate the following flow.

External Systems

↓

Integrations

↓

Business Domains

↓

Inventory Engine

↓

Analytics

↓

Dashboard

Explain how business information progresses through the platform.

Do not describe APIs.

---

# Section 8 – Future Expansion Strategy

Describe how new domains can be added without redesign.

Examples

- Manufacturing
- Production Planning
- CRM
- Vendor Portal
- Barcode Management
- Batch Tracking
- Multi Warehouse
- Mobile App
- AI Recommendations
- Accounting Integration

Explain how future domains should integrate with the existing architecture.

---

# Out of Scope

Do NOT include:

- Database tables
- SQL
- APIs
- REST endpoints
- GraphQL
- Programming language
- Framework
- UI Screens
- Navigation
- Implementation
- Code

These belong to later documents.

---

# Writing Style

Write the document as a professional Enterprise Software Architecture document.

Maintain a technology-independent perspective.

Focus entirely on business domains, responsibilities, ownership, dependencies and scalability.

Avoid implementation details.

The document should become the authoritative architectural blueprint for the AaramBooks Platform.