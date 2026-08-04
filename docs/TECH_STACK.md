# TECH_STACK.md

# AaramBooks Technology Stack

**Version:** 1.0

**Status:** Approved

---

# Purpose

This document defines the official technology stack for the AaramBooks platform.

Its purpose is to ensure that all contributors, including AI assistants, implement the platform using a consistent set of technologies.

Technology decisions documented here are considered project standards.

Do not introduce alternative frameworks or libraries without approval.

---

# Technology Philosophy

The technology stack has been selected based on the following principles:

* Simple to understand.
* Easy to maintain.
* AI-friendly.
* Enterprise-ready.
* Scalable.
* Well documented.
* Large developer ecosystem.
* Strong long-term support.

AaramBooks values **maintainability and developer productivity** over unnecessary technical complexity.

---

# Backend

## Language

Python 3.13+

---

## Framework

FastAPI

Reasons:

* Modern asynchronous framework.
* Excellent performance.
* Automatic OpenAPI documentation.
* Native request validation.
* Strong AI-assisted development support.
* Clean architecture friendly.

---

## API Style

REST API

JSON request and response format.

Future support for GraphQL may be evaluated if required.

---

# Frontend

## Framework

React

---

## Language

TypeScript

Reasons:

* Type safety.
* Better maintainability.
* Excellent tooling.
* Strong AI support.

---

## Build Tool

Vite

Reasons:

* Fast development.
* Modern tooling.
* Excellent React integration.

---

## UI Framework

Material UI (MUI)

Reasons:

* Mature component library.
* Enterprise-grade UI.
* Accessibility support.
* Consistent design system.

Custom business components should extend Material UI rather than replacing it.

---

# Database

## Database Engine

PostgreSQL

Reasons:

* Enterprise-grade reliability.
* ACID compliance.
* Excellent indexing.
* Advanced querying.
* Open source.
* Proven scalability.

SQLite may be used only for local experimentation.

Production deployments shall use PostgreSQL.

---

# ORM

SQLAlchemy 2.x

Reasons:

* Mature ORM.
* Flexible query capabilities.
* Excellent FastAPI integration.
* Supports clean separation between domain and persistence.

---

# Database Migrations

Alembic

Reasons:

* Official migration tool for SQLAlchemy.
* Version-controlled schema changes.
* Repeatable deployments.

All database schema changes shall be performed through Alembic migrations.

Manual database changes are prohibited.

---

# Validation

Pydantic

Reasons:

* Native FastAPI integration.
* Strong type validation.
* Automatic serialization.
* Automatic API documentation.

Business validation rules shall remain within the Domain Layer.

---

# Authentication

JWT (JSON Web Tokens)

Responsibilities:

* User authentication.
* Session management.
* API authorization.

Future enhancements may include:

* OAuth2
* Google Login
* Microsoft Login
* Multi-Factor Authentication (MFA)

---

# Authorization

Role-Based Access Control (RBAC)

Permissions shall be assigned through Roles.

Business authorization rules shall remain inside Business Domains.

---

# Testing

## Backend

pytest

pytest-asyncio

pytest-cov

---

## Frontend

React Testing Library

---

## End-to-End

Playwright

Every Business Object should include:

* Unit Tests
* Integration Tests
* API Tests

Critical business workflows should include End-to-End tests.

---

# API Documentation

FastAPI OpenAPI

Swagger UI

ReDoc

API documentation shall be automatically generated from source code.

---

# Package Management

## Backend

pip

Virtual Environment (venv)

---

## Frontend

npm

---

# Code Quality

## Python

Black

Ruff

isort

mypy

---

## TypeScript

ESLint

Prettier

TypeScript Compiler

Formatting and linting shall be enforced before merging code.

---

# Containerization

Docker

Docker Compose

Every developer should be able to run the complete application locally using a single Docker Compose command.

---

# Version Control

Git

GitHub

Branching Strategy:

* main
* develop
* feature/*
* bugfix/*
* hotfix/*

---

# CI/CD (Future)

GitHub Actions

Pipeline responsibilities:

* Install dependencies.
* Run linting.
* Execute tests.
* Build application.
* Build Docker images.
* Validate migrations.

Deployments will be introduced after the MVP.

---

# Project Structure

The project shall follow a Domain-Driven Design structure.

```text
src/

├── app/
├── foundation/
├── domains/
│   ├── masters/
│   ├── purchases/
│   ├── inventory/
│   ├── accounting/
│   └── reports/
├── infrastructure/
├── shared/
└── ui/
```

Business Domains shall remain isolated.

---

# Design Principles

The implementation shall follow:

* Domain-Driven Design (DDD)
* Clean Architecture
* SOLID Principles
* RESTful API Design
* Business-First Development

Business Rules belong to the Domain Layer.

Infrastructure supports the Domain Layer.

The UI consumes Application Services.

---

# AI Development Guidelines

AI contributors shall:

* Follow the approved architecture.
* Follow this technology stack.
* Never introduce alternative frameworks.
* Never change the technology stack without approval.
* Prefer consistency over novelty.
* Ask for clarification when requirements are incomplete.

---

# Future Technology Decisions

Future additions may include:

* Redis
* Celery
* Elasticsearch
* MinIO
* RabbitMQ
* OpenTelemetry

These technologies shall only be introduced when justified by business requirements.

---

# Technology Freeze

The following technologies are officially approved for Version 1 of AaramBooks:

| Layer             | Technology                                |
| ----------------- | ----------------------------------------- |
| Backend           | Python 3.13                               |
| Backend Framework | FastAPI                                   |
| Frontend          | React                                     |
| Frontend Language | TypeScript                                |
| Build Tool        | Vite                                      |
| UI Framework      | Material UI                               |
| Database          | PostgreSQL                                |
| ORM               | SQLAlchemy                                |
| Migrations        | Alembic                                   |
| Authentication    | JWT                                       |
| Testing           | pytest, React Testing Library, Playwright |
| Containerization  | Docker & Docker Compose                   |

Unless explicitly approved, contributors shall not replace or introduce alternative technologies.

---

# Conclusion

This document defines the official technology stack for AaramBooks Version 1.

All implementation work shall adhere to this stack to ensure consistency, maintainability, and long-term scalability.

The technology stack should remain stable throughout Version 1. Changes should only be made after architectural review and approval.
