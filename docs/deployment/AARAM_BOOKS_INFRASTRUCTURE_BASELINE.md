# AaramBooks Infrastructure Baseline v1.0

This document serves as the absolute source of truth for the AaramBooks production ecosystem. All future microservices and integrations (e.g., AaramPacking, AaramInventory) must adhere to and build upon this certified infrastructure baseline.

## 1. Certified Components

### AaramIdentity (v1.0.0 Production)
- **Status**: Live & Certified
- **Image Source**: `ghcr.io/sums0907/aaramidentity-backend:v1.0.0`
- **Image Source**: `ghcr.io/sums0907/aaramidentity-frontend:v1.0.0`
- **Deployment**: Docker Compose
- **Features**: JWT Authentication, RBAC Authority.

### Gateway (Nginx + SSL)
- **Service**: Nginx Reverse Proxy (Ubuntu System Service)
- **SSL**: Let's Encrypt / Certbot (Automated Renewal)
- **Routing Structure**: `/etc/nginx/sites-available/`

### Production Domains
- **Frontend**: `https://identity.aarambooks.cloud`
- **Backend API**: `https://api.identity.aarambooks.cloud`

### Database Ecosystem
- **Engine**: PostgreSQL 16 (Bare-metal installation)
- **Database Name**: `identity_prod`
- **Migration Origin**: Upgraded from legacy SQLite

## 2. Backup & Disaster Recovery (v1.0)
The fully automated Backup & Disaster Recovery system is active and verified.

### Backup Capabilities
- Automated daily backup via `crontab` (`02:00 AM`)
- Strict retention management (7 Daily / 4 Weekly)
- Encrypted secrets backup (RSA Keys)
- Deployment configuration snapshots
- Nginx routing configurations backup
- Formal Restore Validation completed.

## 3. Operational Hardening (v1.0)
The environment has been actively hardened to guarantee long-term stability under the strict storage constraints.

### Certified Hardening Features
- **Docker Log Rotation**: Verified as natively configured (`max-size: 10m`, `max-file: 3`) globally via `/etc/docker/daemon.json`.
- **Proactive Disk Monitoring**: `disk_monitor.sh` implemented to continuously track root, Docker, PostgreSQL, and backup storage footprints with 20% warning and 10% critical thresholds.
- **Operations Runbook**: `OPERATIONS_RUNBOOK.md` established to dictate safe Docker cleanup policies, health verification, and restart procedures without risking production state.

## 4. Strict Infrastructure Constraints
**IMPORTANT PERMANENT CONSTRAINT:**
- **Host**: Hostinger VPS KVM 1
- **Storage Limit**: 50GB NVMe Disk
- **Memory Management**: 2GB Swap exists (NOT for storage/backup)

*Note: No storage expansion is planned. All backups, deployments, and future services must strictly monitor their footprint to guarantee they never threaten the 50GB ceiling.*
