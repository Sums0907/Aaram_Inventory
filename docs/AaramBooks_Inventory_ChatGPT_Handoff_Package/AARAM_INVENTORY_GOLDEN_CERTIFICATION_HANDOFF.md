# AARAMBOOKS INVENTORY — GOLDEN CERTIFICATION HANDOFF

## Certification Project
`/Users/sumatidhingra/Documents/Aaram_IntegrationCertification`

## Purpose
Independent validation of:
`AaramPackingApp` + `Aaram_Inventory`

## Required Flow
```text
Golden Certification
       |
       +------------------+
       |                  |
       v                  v
Aaram Packer         Aaram Inventory
       |                  |
       +------ HTTP ------+
```

## Production Path Requirement
Prefer:
Packer real workflow -> Packer outbox -> dispatcher -> real HTTP -> Inventory receiver -> Inventory service -> Inventory ledger.

Do not replace the entire path with direct database inserts or duplicated business logic.

## Artifacts
All generated reports/logs/snapshots must be inside the certification project, preferably:
```text
artifacts/<timestamp>/
```

Do not pollute either application root.

## Current Status
Both applications have implemented outbound/receiver integration paths. The independent certification workspace must first perform read-only discovery of actual startup, test database, test data and observation interfaces before implementing the Golden Suite.
