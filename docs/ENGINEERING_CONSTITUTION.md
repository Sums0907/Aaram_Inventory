# AaramBooks Engineering Constitution

Version: 1.0

Status: Mandatory

Audience:
- AI Software Engineers
- Human Developers
- Architects
- Contributors

---

# Purpose

This Constitution defines the engineering principles that govern every implementation decision within the AaramBooks Platform.

It exists to ensure that implementation always follows the Business Architecture.

The architecture is considered the source of truth.

Implementation exists only to realize the architecture.

No implementation may redefine the architecture.

---

# Mission

Every line of code written for AaramBooks shall:

• Preserve Business Architecture.

• Preserve Domain Boundaries.

• Preserve Business Ownership.

• Preserve Event Driven communication.

• Preserve Information Integrity.

• Preserve Technology Independence.

The goal is not merely to produce working software.

The goal is to produce software that faithfully implements the Business Architecture.

---

# Principle 1
## Architecture First

Architecture always precedes implementation.

Implementation shall never introduce architectural decisions.

If implementation requires a new architectural decision:

STOP.

Update the Architecture first.

Only then continue implementation.

---

# Principle 2
## Business First

Business drives software.

Software never drives business.

Business terminology shall always be used.

Examples:

Supplier

Warehouse

Material Receipt

Current Stock

Purchase Invoice

Sale

Inventory Adjustment

Avoid technical terminology replacing business terminology.

---

# Principle 3
## Business Model is Supreme

The Business Model is the highest authority.

No implementation may contradict:

Business Vision

Business Objectives

Business Policies

Business Domains

Business Governance

If implementation conflicts with the Business Model:

The implementation is wrong.

---

# Principle 4
## System Architecture is Law

System Architecture defines:

Business Domains

Ownership

Dependencies

Communication

Layers

No implementation may violate these boundaries.

---

# Principle 5
## Information Model Owns Business Information

Business Objects exist only because they are defined in the Information Model.

Developers shall never invent:

Business Objects

Business Relationships

Business Rules

Business Lifecycles

If something is missing:

Update the Information Model.

---

# Principle 6
## Data Dictionary Owns Business Attributes

Every Business Attribute must exist in the Data Dictionary.

Developers shall never invent:

Columns

Properties

Fields

Attributes

Flags

Status Values

Derived Values

If an attribute does not exist:

Update the Data Dictionary first.

---

# Principle 7
## Single Source of Truth

Every business concept shall have exactly one Authoritative Owner.

Never duplicate ownership.

Examples:

Inventory Engine owns Current Stock.

Masters own Supplier.

Procurement owns Purchase Invoice.

Reports consume information.

Reports never own information.

---

# Principle 8
## Respect Domain Boundaries

Every Domain owns its responsibilities.

Never move responsibilities across Domains.

Never duplicate Domain responsibilities.

Never bypass Domain ownership.

---

# Principle 9
## No Cross-Domain Database Access

Domains collaborate through architecture.

Never access another Domain's persistence directly.

Communication shall occur through defined interfaces and Business Events.

---

# Principle 10
## Event Driven by Default

Business behaviour is represented through Business Events.

Business state changes should occur because of Business Events.

Never update derived information directly.

Derived information must be produced from Business Events.

---

# Principle 11
## Inventory is Derived

Current Stock is never edited.

Current Stock is calculated.

Inventory exists because Business Events occurred.

Direct inventory editing is prohibited.

---

# Principle 12
## Reports Never Become Operational Systems

Reports consume information.

Reports never create business information.

Reports never modify Business Objects.

Reports remain read-only.

---

# Principle 13
## Masters are Stable

Master Data changes slowly.

Operational Data changes frequently.

Never mix Master Data with Operational Data.

---

# Principle 14
## No Business Logic in UI

UI collects information.

UI displays information.

Business Decisions belong elsewhere.

UI shall never:

calculate inventory

decide business rules

validate business policies

perform business calculations

---

# Principle 15
## No Business Logic in Infrastructure

Infrastructure stores.

Infrastructure retrieves.

Infrastructure integrates.

Infrastructure never decides.

---

# Principle 16
## Application Layer Orchestrates

Application Layer coordinates work.

It never owns Business Rules.

It never owns Business Policies.

Business knowledge belongs inside the Domain Layer.

---

# Principle 17
## Small Aggregates

Each Aggregate should represent one Business Object.

Avoid giant object graphs.

Keep aggregates cohesive.

---

# Principle 18
## Rich Domain

Business Rules belong inside the Domain.

Avoid procedural services containing business knowledge.

Business behaviour should live beside Business Objects.

---

# Principle 19
## Immutable Business History

Business history should never be rewritten.

Corrections occur through new Business Events.

Not by editing historical records.

---

# Principle 20
## Business Before Optimization

Correctness is more important than speed.

Optimize only after correctness has been achieved.

Never sacrifice business integrity for performance.

---

# Principle 21
## Documentation Before Code

Every significant change shall first update:

Business Model

System Architecture

Event Model

Information Model

Data Dictionary

Only after documentation is complete may implementation begin.

---

# Principle 22
## One Domain at a Time

Implementation shall proceed Domain by Domain.

Recommended order:

Masters

↓

Procurement

↓

Operations

↓

Inventory Intelligence

↓

Reports & Analytics

↓

Pending Operations

↓

Platform Administration

Each Domain should be fully completed before the next Domain begins.

---

# Principle 23
## Vertical Slice Development

For every Domain follow this sequence:

Information Model

↓

Data Dictionary

↓

Database Model

↓

API Design

↓

UI Design

↓

Implementation

↓

Testing

↓

Documentation

Never skip stages.

---

# Principle 24
## No Guessing

Developers shall never invent:

Business Rules

Business Policies

Business Objects

Business Attributes

Domain Responsibilities

Report Calculations

Status Values

Workflow Steps

If something is unclear:

Ask.

Do not guess.

---

# Principle 25
## Explain Decisions

Every implementation should be understandable.

Prefer clarity over cleverness.

Future developers should immediately understand why the solution exists.

---

# Principle 26
## AI Development Rules

When implementing AaramBooks, the AI shall:

Never invent architecture.

Never change Business Models.

Never rename Business Objects.

Never introduce hidden assumptions.

Never merge Domains.

Never bypass ownership.

Never violate layering.

When uncertain:

Stop and ask.

---

# Principle 27
## Code Review Checklist

Before any implementation is accepted verify:

✓ Architecture preserved

✓ Domain ownership respected

✓ Business terminology correct

✓ No invented Business Objects

✓ No invented attributes

✓ No duplicated Business Rules

✓ No cross-domain violations

✓ Event Model respected

✓ Information Model respected

✓ Documentation updated

---

# Principle 28
## Long-Term Thinking

Every implementation decision should ask:

Will this still make sense in five years?

Will another developer understand it?

Does it preserve the architecture?

Can it evolve safely?

If not,

choose another design.

---

# Final Statement

The AaramBooks Architecture is the product.

The software is an implementation of that architecture.

Every contributor—human or AI—is responsible for preserving the integrity of the Business Model, System Architecture, Event Model and Information Model.

No implementation convenience shall take precedence over architectural correctness.

When architecture and implementation disagree,

**the architecture always wins.**