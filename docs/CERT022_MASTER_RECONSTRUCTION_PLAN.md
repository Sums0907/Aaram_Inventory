# CERT-022 Master Data Reconstruction Plan

## 1. Workbook Analysis
The source workbook `AaramBooks_Master_Data.xlsx` contains a mixed master dataset representing both Raw Material (RM) and Finished Goods (FG) domains.
The sheets and columns identified are:
- **Instructions**: Key, Value
- **UoM**: UoM Code, UoM Name, Short Name, Type, Description
- **Suppliers**: Phone Number, Supplier Name, GSTIN, Email, Address, Remarks, Is Job Worker
- **Inventory_Categories**: Category Code, Category Name, Item Type, Parent Category Code, Description, Status
- **Category_Attributes**: Category Code, Attribute Code, Attribute Name, Is Required, Description
- **Inventory_Items**: Item Code, Item Name, Item Type, Category Code, Base UoM Code, Barcode, Description, Status
- **BOM**: BOM Number, BOM Name, Finished SKU, Base Quantity, Component Item Code, Component Quantity, Wastage %

**Data Conflicts/Observations**:
- `Item Type` is likely the primary discriminator for filtering FG vs. RM domain data in `Inventory_Categories` and `Inventory_Items`.
- `BOM` links FG items (`Finished SKU`) with RM items (`Component Item Code`). The RM sub-engine must process BOM dependencies without attempting to assume ownership of the FG SKUs.

## 2. Test Datasets Required
We will split the mixed dataset into two certification datasets:

### A. RM_MASTER_CERTIFICATION_DATA.xlsx
Contains only Raw Material domain entities:
- UoM
- Suppliers
- Operational Categories (Filtered by Item Type = RM/Operational)
- Raw Materials (Filtered by Item Type = RM)
- Valid RM BOM dependencies

### B. FG_BOUNDARY_CERTIFICATION_DATA.xlsx
Contains only Finished Goods domain entities:
- Finished Goods items (Filtered by Item Type = FG)
- Finished Goods category data

*Purpose*: Verify the Raw Material Sub-Engine rejects/excludes FG-owned data and enforces domain boundaries.

## 3. Implementation Plan

### CERT-022A: Raw Material Full Reconstruction Test
**Flow**:
1. Original Excel `RM_MASTER_CERTIFICATION_DATA.xlsx`
2. Import via Sub-Engine Importer
3. Database A (Populated)
4. Export Database A to Excel
5. Fresh Database B
6. Import Exported Excel into Database B
7. Compare Database A and Database B

**Verification**:
- Assert absolute equality for: UOM, Supplier, Category hierarchy, Raw Material items, BOM.
- Ignored Fields: internal IDs, timestamps, audit records.

### CERT-022B: Finished Goods Boundary Test
**Flow**:
1. Original Excel `FG_BOUNDARY_CERTIFICATION_DATA.xlsx`
2. Attempt Import via RM Sub-Engine Importer
3. Verify rejection logs and boundary enforcement.

**Verification**:
- Assert RM engine cannot import FG categories, FG SKUs, or external catalogue fields (e.g., ShopDeck integrations).
