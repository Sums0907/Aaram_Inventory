# CONTRIBUTING.md

# AaramBooks Development Constitution

**Version:** 1.0

---

# Welcome

Welcome to the AaramBooks project.

AaramBooks is an enterprise-grade accounting and inventory platform built using Domain-Driven Design (DDD), Clean Architecture and Business-First principles.

Every contributor—human or AI—is expected to follow the standards defined in this document.

The objective is not merely to write working software.

The objective is to build software that faithfully represents the business architecture while remaining simple, maintainable and extensible.

---

# Core Philosophy

The architecture is the source of truth.

Implementation exists to realize the architecture.

If implementation and architecture conflict, the architecture takes precedence.

Never change business behaviour through code alone.

Architecture changes must always precede implementation changes.

---

# Engineering Principles

Every contribution shall follow these principles.

## Business First

Business concepts drive implementation.

Technology serves the business.

Never allow technical convenience to redefine business behaviour.

---

## Simplicity

Prefer the simplest solution that satisfies the documented requirements.

Avoid unnecessary abstraction.

Avoid premature optimization.

Avoid over-engineering.

---

## Explicitness

Business behaviour should always be obvious.

Avoid hidden logic.

Avoid magic values.

Avoid implicit side effects.

---

## Consistency

Follow existing patterns.

Do not introduce new coding styles, naming conventions or architectural patterns unless explicitly approved.

---

# Source of Truth

The following documents define the project.

1. Business Model
2. System Architecture
3. Event Model
4. Information Model
5. Engineering Constitution
6. Domain READMEs

These documents are authoritative.

Implementation shall never contradict them.

---

# Business Objects

Business Objects are defined in their respective domain documents.

Do not:

* invent Business Objects
* rename Business Objects
* merge Business Objects
* split Business Objects

without updating the architecture first.

---

# Business Rules

Business Rules belong inside the Domain Layer.

Never place business logic inside:

* Controllers
* API Routes
* Database Queries
* UI Components

Business Rules should be reusable, testable and independent of infrastructure.

---

# Domain Boundaries

Every Business Object belongs to exactly one Business Domain.

Do not duplicate ownership across domains.

Cross-domain communication shall occur through well-defined interfaces or business events.

---

# Folder Structure

Follow the approved project structure.

Do not reorganize folders without approval.

Business Domains should remain isolated.

Shared functionality belongs only in shared modules.

---

# Naming Standards

Use business terminology.

Good examples:

* InventoryItem
* Supplier
* Warehouse
* PurchaseInvoice

Avoid technical or ambiguous names such as:

* Manager
* Helper
* Processor
* DataHandler
* Utils2

Names should describe business intent.

---

# Coding Standards

Code should be:

* Small
* Readable
* Predictable
* Testable
* Self-documenting

Avoid unnecessary comments.

Prefer expressive code over explanatory comments.

---

# Dependencies

Dependencies should always point inward.

Business Domains must not depend on UI or infrastructure.

Infrastructure depends on Business Domains.

UI consumes Application Services.

---

# API Guidelines

APIs should expose business capabilities.

Do not expose database structures directly.

Use business terminology in endpoints, requests and responses.

Maintain consistent response formats.

---

# Database Guidelines

Database schema shall reflect the approved Information Model.

Never introduce columns or tables that are not backed by documented Business Attributes.

Avoid storing derived data unless explicitly approved.

---

# UI Guidelines

UI should reflect business workflows.

Do not embed business logic in UI components.

UI is responsible only for presentation and user interaction.

---

# Testing

Every Business Object shall include tests.

Minimum expectations:

* Business Rule tests
* Validation tests
* API tests
* Integration tests

Bug fixes must include regression tests where appropriate.

---

# Documentation

Whenever business behaviour changes:

Update the documentation first.

Then update the implementation.

Documentation and implementation must always remain synchronized.

---

# Git Guidelines

Keep commits focused.

One logical change per commit.

Use descriptive commit messages.

Examples:

* Add Company Business Object
* Implement Warehouse APIs
* Validate Inventory Item creation
* Fix SKU uniqueness validation

Avoid combining unrelated changes.

---

# Pull Requests

Every Pull Request should:

* Address one logical feature or fix.
* Preserve architecture.
* Pass all tests.
* Update documentation if required.

Large unrelated Pull Requests should be avoided.

---

# Code Review Checklist

Before merging, verify:

* Architecture compliance
* Business Rules implemented correctly
* Naming consistency
* Test coverage
* Documentation updates
* No duplicated logic
* No unnecessary complexity

---

# AI Contributor Guidelines

AI assistants shall:

* Implement only documented requirements.
* Never invent Business Objects.
* Never invent Business Rules.
* Never assume missing behaviour.
* Ask for clarification whenever documentation is insufficient.
* Preserve existing architecture.
* Prefer consistency over creativity.

The role of AI is to implement the architecture—not redesign it.

---

# Definition of Done

A feature is complete only when:

* Business behaviour is implemented.
* Tests pass.
* Documentation is updated.
* Architecture remains compliant.
* Code review is complete.

Working code alone does not constitute completion.

---

# Final Principle

Every contribution should leave the codebase simpler, clearer and more maintainable than it was before.

When in doubt:

**Choose the solution that best reflects the documented business architecture, not the one that is merely easiest to implement.**
