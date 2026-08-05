# Inventory Business Objects

## Purpose

This directory contains the detailed functional specifications for every Business Object within the Inventory Domain.

While `docs/inventory/README.md` defines the architecture, responsibilities, and guiding principles of the Inventory Engine, the documents in this folder define the behavior of each individual Business Object.

Every Business Object document acts as the single source of truth for implementation.

Developers, architects, AI coding agents, and testers should refer to these specifications before writing or modifying code.

---

# Business Objects

## 01. Inventory Movement

Represents an immutable inventory transaction.

Every stock change within the system must originate from an Inventory Movement.

Examples include:

* Opening Stock
* Purchase
* Sale
* Customer Return
* Supplier Return
* Warehouse Transfer
* Stock Adjustment
* Manufacturing
* Reservation
* Reservation Release

This is the most important Business Object in the Inventory Domain.

---

## 02. Inventory Balance

Represents the calculated stock position of a SKU within a warehouse.

Inventory Balance is derived from Inventory Movements and should never be edited directly.

It provides:

* Quantity On Hand
* Reserved Quantity
* Available Quantity

---

## 03. Stock Reservation

Represents inventory temporarily allocated to customer orders.

Reserved inventory is unavailable for allocation to other orders until released or fulfilled.

Reservations do not modify physical inventory.

---

## 04. Stock Transfer

Represents the movement of inventory between warehouses.

A transfer always generates two Inventory Movements:

* Transfer Out
* Transfer In

The overall inventory of the organization remains unchanged.

---

## 05. Stock Adjustment

Represents manual corrections to inventory.

Examples include:

* Physical stock verification
* Damaged goods
* Lost inventory
* Found inventory
* Inventory write-off

Every adjustment must record the reason, user, and timestamp.

---

# Specification Structure

Every Business Object specification follows a consistent structure.

* Purpose
* Responsibilities
* Business Attributes
* Validation Rules
* Business Rules
* Relationships
* Lifecycle
* Status Definitions
* API Endpoints
* Permissions
* Events
* Reporting Impact
* Examples
* Future Enhancements

This standardized structure ensures consistency across the entire AaramBooks platform.

---

# Design Principles

All Inventory Business Objects follow these principles:

* Single Responsibility
* Immutable Business Events
* Deterministic Behaviour
* Complete Auditability
* Warehouse Awareness
* SKU-Centric Design
* Event-Driven Processing

No Business Object should duplicate responsibilities that belong to another object.

---

# Implementation Order

Business Objects should be implemented in the following sequence:

1. Inventory Movement
2. Inventory Balance
3. Stock Reservation
4. Stock Transfer
5. Stock Adjustment

Each Business Object should be fully implemented—including Models, Schemas, Repositories, Services, APIs, Tests, and Documentation—before moving to the next.

---

# Versioning

Business Object specifications evolve alongside the Inventory Domain.

Changes to these documents must preserve backward compatibility whenever possible.

Breaking business rule changes should be documented explicitly and reflected in the project CHANGELOG.

---

# Guiding Principle

The Inventory Domain is built around one central concept:

**Every inventory change is an Inventory Movement.**

All other Business Objects either derive information from these movements or manage how those movements are created and controlled.
