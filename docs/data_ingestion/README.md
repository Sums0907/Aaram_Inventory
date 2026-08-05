# Data Ingestion Domain Architecture

**Domain:** Data Ingestion (Formerly Integrations)  
**Version:** 1.0  
**Status:** Approved Architecture

---

## 1. Objective

The Data Ingestion Domain is the true core of AaramBooks. It serves as a generic, canonical pipeline that transforms messy, unstructured marketplace data (from CSVs, APIs, Webhooks) into a standardized business model. 

AaramBooks is an **e-commerce accounting automation platform**. This domain automates the ingestion of sales, settlements, and refunds to eliminate manual data entry.

## 2. Canonical Business Pipeline

The Data Ingestion engine does not think about "CSV rows". It thinks in terms of a strict business pipeline. Regardless of whether data comes from a ShopDeck CSV, a Razorpay API, or a Shiprocket Webhook, it flows through the exact same canonical pipeline:

```text
Upload File / Receive API Payload
       ↓
Create Import Job
       ↓
Validate Source
       ↓
Read & Normalize Records
       ↓
Validate Business Rules
       ↓
Persist Canonical Data
       ↓
Generate Import Summary
       ↓
Ready for Settlement Engine
```

## 3. Core Business Objects

The domain defines its own canonical business objects. Every integration maps into this exact model:

1. **Integration:** Defines the external platform (e.g., ShopDeck, Amazon) and its configuration rules.
2. **Import Job:** The root aggregate. Tracks the import source, file name, status, total records, successes, and failures.
3. **Import Batch:** (Optional) For chunking large jobs.
4. **Import Record:** A single raw record within a job.
5. **Import Error:** Tracks validation failures for auditing.
6. **Sales Order:** The canonical representation of a marketplace sale.
7. **Settlement:** The financial breakdown of a payout (fees, shipping, net payout).
8. **Payment:** The actual cash movement record.
9. **Refund:** The financial record of returned funds.

## 4. Extensibility

By enforcing this canonical model, the Data Ingestion Engine becomes a reusable capability. Adding a new integration (e.g. Amazon Settlement API) simply requires writing a new Adapter that maps Amazon's JSON payload into our canonical `Import Record` -> `Settlement` objects, plugging seamlessly into the existing pipeline.
