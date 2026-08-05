# Operations Domain

## Purpose

The Operations Domain is the transactional heart of AaramBooks. 
While the Data Ingestion Engine handles the chaotic reality of external CSVs and APIs, the Operations Domain serves as the **canonical, structured staging ground** for all core business activities. 

Its ultimate vision is to power a full-scale Inventory Intelligence platform. In Version 1, it acts as the necessary bridge between raw E-commerce data (ShopDeck/Razorpay) and the Accounting Engine (Vyapar), allowing AaramBooks to solve immediate e-commerce accounting pain points without limiting future expansion into warehouse management, stock adjustments, and purchasing.

---

## Business Objects

The initial rollout (Version 1) focuses strictly on downstream commerce entities to support e-commerce accounting. 

### 1. `SalesOrder` & `SalesOrderItem`
- **Definition:** Represents a customer's intent to purchase and the associated financial totals.
- **Granularity:** Line items (`SalesOrderItem`) are modeled as strict relational SQL tables to enable precise SKU-level analytics and future inventory reservations.

### 2. `TaxInvoice` & `TaxInvoiceItem`
- **Definition:** The authoritative fiscal document required for tax compliance. 
- **Granularity:** While a `SalesOrder` tracks what was sold, the `TaxInvoice` dictates how it is taxed (HSN Codes, IGST/CGST/SGST splits). 

### 3. `Payment`
- **Definition:** An individual money movement (e.g., a single Razorpay transaction).
- **Attributes:** Captures gross transaction amount, payment gateway fees, tax on fees, and the net amount.

### 4. `Settlement`
- **Definition:** A batch transfer arriving at the corporate bank account.
- **Attributes:** Captures the UTR number, total gross, batch fees, and net remittance. Represents both COD logistics payouts and Gateway payouts.

### *(Future Expansion Objects)*
- `PurchaseOrder`, `GoodsReceiptNote (GRN)`, `StockMovement`, `ReturnOrder`, `InventoryAdjustment`.

---

## Relationships

1. **Items to Catalogs:** `SalesOrderItem` and `TaxInvoiceItem` contain a `sku_id` referencing the `Master` catalog. **Constraint:** This foreign key must remain nullable during V1 to allow ingestion of external orders even if the exact SKU hasn't been mapped internally yet.
2. **Invoices to Orders:** A `TaxInvoice` belongs to a single `SalesOrder`.
3. **Payments to Settlements:** Multiple `Payment` records roll up into a single `Settlement`.

---

## Lifecycle

Operations objects are created by the **Commit Engine** (consuming `ImportRecord`s) and then undergo state transitions managed by downstream engines:

1. **`UNMATCHED`:** The default state upon creation. For example, a Razorpay Payment enters as `UNMATCHED` because the system does not yet know which `SalesOrder` it belongs to.
2. **`MATCHED`:** The Matching Engine successfully links the object to its counterpart (e.g., Payment to Order).
3. **`ACCOUNTED`:** The Accounting Engine has successfully generated General Ledger journals for this object.

---

## Business Rules

1. **Pure Persistence:** The Operations Domain does *not* invent data. It strictly persists the normalized data provided by the Data Ingestion Committers.
2. **Deferred Reconciliation:** No assumptions are made during ingestion. If a Razorpay file does not explicitly and cleanly link to a ShopDeck Order ID, the `Payment` is created as `UNMATCHED`. 
3. **Strict Line Items:** All transactional line items must be stored as relational rows, never as flattened JSON arrays. This is the non-negotiable foundation for building Inventory Intelligence.
4. **Immutability of Financials:** Once an Operations object reaches the `ACCOUNTED` state, its core financial amounts (`gross`, `tax`, `fees`, `net`) cannot be mutated.

---

## Events

The Operations domain acts as the trigger for the rest of the ecosystem.
- `SalesOrderCommitted` -> Triggers the Matching Engine (and future Inventory Reservation).
- `TaxInvoiceCommitted` -> Triggers the Accounting Engine to recognize revenue and tax liability.
- `SettlementCommitted` -> Triggers the Matching Engine to reconcile Payments against the bank UTR.
