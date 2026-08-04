# Aaram_Inventory AI Agent Rules

- **Foundation Layer Freeze**: The `src/foundation/` layer is explicitly FROZEN. Do NOT modify any code in this layer unless explicitly instructed by the user with a compelling reason. The architecture is locked and must act strictly as generic, reusable infrastructure for the business domains.
- **Versioning Strategy**: `APP_VERSION` must only represent actual application releases (e.g., `0.1.0`, `0.2.0`). Do not use `APP_VERSION` to track implementation milestones of single Business Objects. Use Git tags (e.g., `v0.2.0-company`) for tracking implementation milestones instead.
