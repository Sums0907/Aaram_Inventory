# AARAMBOOKS SKU MASTER DATA IMPORT/EXPORT SUB-ENGINE

## AARAMBOOKS_SKU_MASTER_DATA_IMPORT/EXPORT SUB-ENGINE.md

Version: `SKU_MASTER_SYNC_V1`

Status: Architecture Definition  
Owner: AaramBooks SKU Master Synchronisation Module  
Source System: ShopDeck Master Catalogue CSV  
Target System: AaramBooks Inventory System

---

# 1. Purpose

The SKU Master Data Import/Export Sub-Engine is responsible for synchronising **Finished Goods catalogue data** from ShopDeck into AaramBooks.

It manages:

- Finished Goods SKUs
- Finished Goods catalogue attributes
- Finished Goods category mapping
- Product metadata
- Pricing information
- Packaging information

It does **not** manage inventory quantities.

The purpose is to maintain:

```
ShopDeck Catalogue
        |
        |
        ↓
SKU Master Synchronisation Engine
        |
        |
        ↓
AaramBooks Finished Goods Master
```

---

# 2. Important Architectural Boundary

AaramBooks has two different master data ownership domains.

```
AaramBooks Master Data Framework


                |
                |
------------------------------------------------

                |
                |

Raw Material Master                 SKU Master
Import/Export                       Synchronisation
Sub-Engine                          Sub-Engine


AaramBooks Owned                    ShopDeck Owned
```

---

## Raw Material Domain

Controlled by:

```
AaramBooks
```

Includes:

- Raw Materials
- Packaging
- Consumables
- Assets
- Suppliers
- BOM

---

## SKU Domain

Controlled by:

```
ShopDeck Catalogue
```

Includes:

- Finished Goods SKUs
- Finished Goods Categories
- Catalogue attributes
- Product metadata

---

# 3. Source of Truth

## ShopDeck is the source of truth for:

- SKU existence
- SKU identity
- Product Code
- Product Name
- Attributes
- Pricing
- Packaging information
- Catalogue categories


## AaramBooks is the source of truth for:

- Inventory quantity
- Stock ledger
- Available inventory
- Physical stock
- Warehouse stock
- Inventory movements

---

# 4. Critical Rule — Inventory Quantity

## ShopDeck Quantity MUST BE IGNORED

CSV field:

```
Quantity
```

must never be imported.

It must never:

- update inventory
- update SKU master
- affect stock calculation
- participate in comparison
- participate in export/import round trips


Reason:

ShopDeck quantity is not actual inventory.

It may be:

- manually adjusted
- inflated
- maintained only to avoid website showing out-of-stock


Therefore:

```
ShopDeck Quantity

        ≠

AaramBooks Inventory Quantity
```

---

# 5. SKU Identity Model

## Primary Immutable Identity

Only:

```
ShopDeck Sku Id
```

is the permanent identity.

Example:

```
Sku Id:
123456789
```

Matching rule:

```
Incoming Sku Id
        |
        ↓
Existing AaramBooks SKU
```

---

# 6. Product Code Rule

Product Code is owned by ShopDeck.

However:

```
Product Code is mutable
```

It can change.

Example:

Before:

```
Sku Id:
10001

Product Code:
BED-001
```

After:

```
Sku Id:
10001

Product Code:
BED-PREMIUM-001
```

This is NOT a new SKU.

Action:

```
UPDATE Product Code
```

---

# 7. Field Governance Matrix

## Immutable Identity Fields

| Field | Rule |
|-|-|
| ShopDeck Sku Id | Never changes |

---

## Mutable Fields

These are updated from latest ShopDeck snapshot.

| Field | Action |
|-|-|
| Product Code | Update |
| Amazon ASIN | Update |
| Name | Update |
| Selling Price | Update |
| MRP | Update |
| Cost Price | Update |
| Packaging Length | Update |
| Packaging Breadth | Update |
| Packaging Height | Update |
| Packaging Weight | Update |
| GST % | Update |
| Attributes | Update |
| Category Path | Synchronise |

---

## Ignored Fields

| Field | Rule |
|-|-|
| Quantity | Completely ignored |

---

# 8. Synchronisation Behaviour

Each ShopDeck CSV is treated as a snapshot.

Example:

Month 1:

```
SKU-101
SKU-102
SKU-103
```

Month 2:

```
SKU-101
SKU-103
SKU-104
```

---

# 9. New SKU Handling

Condition:

```
Sku Id does not exist in AaramBooks
```

Action:

```
CREATE SKU
```

Imported:

- Sku Id
- Product Code
- Name
- Attributes
- Pricing
- Packaging
- Category mapping

Ignored:

- Quantity

---

# 10. Existing SKU Handling

Condition:

```
Sku Id exists
```

Action:

```
UPDATE mutable attributes
```

Example:

Existing:

```
Sku Id:
10001

Name:
Blue Bedsheet

Selling Price:
1499
```

New CSV:

```
Sku Id:
10001

Name:
Premium Blue Bedsheet

Selling Price:
1699
```

Result:

```
Same SKU

Updated:
Name
Selling Price
```

---

# 11. Missing SKU Handling

Important:

Missing SKU does NOT mean delete.

Example:

Database:

```
10001
10002
10003
```

New ShopDeck CSV:

```
10001
10003
```

SKU:

```
10002
```

Action:

```
ARCHIVE / INACTIVE
```

Never:

```
DELETE
```

Reason:

SKU may have:

- orders
- inventory movements
- historical reports
- accounting references

---

# 12. Finished Goods Category Synchronisation

Finished Goods categories belong to this sub-engine.

They are NOT handled by:

```
Raw Material Category Importer
```

Ownership:

```
ShopDeck Catalogue
```

---

# Category Ownership Rule

Category ownership is determined by hierarchy.

Never use:

```
Category.item_type
```

because historical database values may be incorrect.

---

Authoritative method:

```
Category hierarchy
        |
        ↓
Root ancestor category_code
```

---

Root categories:

```
FG  = Finished Goods
RM  = Raw Materials
PKG = Packaging
CON = Consumables
AST = Assets
```

---

Example:

```
FG
 |
 Bedding
      |
      Bedsheets
```

Domain:

```
FINISHED_GOODS
```

---

# 13. SKU Synchronisation Flow

```
ShopDeck CSV

      |
      ↓

CSV Validation

      |
      ↓

Extract Sku Ids

      |
      ↓

Identity Matching

      |
      |
-----------------------------
|                           |
Existing SKU             New SKU

|                           |

Update fields             Create


      |
      ↓

Missing SKU Detection

      |
      ↓

Archive missing records
```

---

# 14. Validation Rules

Before commit:

Validate:

## Identity

- Sku Id exists
- Duplicate Sku Id rejected


## Product Code

Allowed:

```
Change
```

because mutable.


## Quantity

Always ignored.


## Category

Validate:

- Finished Goods hierarchy only
- Reject operational category mapping


---

# 15. Export Rules

SKU Export is not the same as Raw Material Export.

Future SKU exporter should export:

- Current SKU state
- Catalogue attributes
- ShopDeck identifiers

It should NOT export:

```
Inventory Quantity
```

because inventory belongs to AaramBooks.

---

# 16. Audit Requirements

Every synchronization run should record:

```
SKU_SYNC_BATCH
```

with:

- File name
- Import date
- Number of created SKUs
- Number updated
- Number archived
- Number rejected
- Executing user

---

# 17. Recommended Module Structure

```
src/domains/sku_master_sync/


    shopdeck_reader.py


    sku_matcher.py


    sku_validator.py


    sku_creator.py


    sku_updater.py


    sku_archiver.py


    finished_goods_category_sync.py


    sku_exporter.py
```

---

# 18. Testing Requirements

## Identity Tests

### SKU-001

Same Sku Id:

Expected:

```
UPDATE
```

not CREATE.


---

### SKU-002

Changed Product Code with same Sku Id:

Expected:

```
UPDATE Product Code
```

---

### SKU-003

New Sku Id:

Expected:

```
CREATE
```

---

## Quantity Protection Tests

### SKU-004

ShopDeck Quantity differs.

Example:

Before:

```
Inventory:
25
```

CSV:

```
Quantity:
500
```

Expected:

```
Inventory remains 25
```

---

## Missing SKU Tests

### SKU-005

SKU absent from latest snapshot.

Expected:

```
ARCHIVE
```

not DELETE.

---

## Category Tests

### SKU-006

FG hierarchy accepted.

### SKU-007

RM hierarchy rejected.

---

# 19. Golden Synchronisation Principle

The SKU Master Sub-Engine must maintain:

```
ShopDeck Catalogue Truth

+
AaramBooks Inventory Truth

without mixing them
```

The most important invariant:

```
SKU Identity comes from ShopDeck.

Inventory Quantity comes from AaramBooks.
```

---

# Final Architecture

```
                 AARAMBOOKS MASTER DATA FRAMEWORK


                          |
                          |

        ---------------------------------------
        |                                     |
        |                                     |

Raw Material Master                  SKU Master
Import/Export                        Synchronisation
Sub-Engine                           Sub-Engine


AaramBooks Controlled                 ShopDeck Controlled


```

---

## Status

Architecture frozen.

Implementation should begin only after approval of this README.

The first implementation milestone should be:

**SKU Master Synchronisation Dry-Run Engine**

before any database mutation is allowed.
