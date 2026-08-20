import pandas as pd
import os

SOURCE_FILE = "AaramBooks_Master_Data.xlsx"
OUT_DIR = "tests/data"

def get_root_domain(cat_code, cat_dict):
    current = cat_code
    visited = set()
    while current in cat_dict:
        if current in visited:
            break # cycle
        visited.add(current)
        parent = cat_dict[current].get("Parent Category Code")
        if pd.isna(parent) or not parent or str(parent).strip() == "":
            return cat_dict[current].get("Item Type")
        current = parent
    return None

def main():
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
        
    xl = pd.ExcelFile(SOURCE_FILE)
    sheets = {sheet: xl.parse(sheet) for sheet in xl.sheet_names}
    
    # Process Categories to find roots
    cat_df = sheets.get("Inventory_Categories", pd.DataFrame())
    
    cat_dict = {}
    for _, row in cat_df.iterrows():
        cat_dict[row["Category Code"]] = row.to_dict()
        
    fg_cats = set()
    rm_cats = set()
    
    for cat_code in cat_dict.keys():
        root_type = get_root_domain(cat_code, cat_dict)
        if root_type == "FINISHED_GOODS":
            fg_cats.add(cat_code)
        else:
            rm_cats.add(cat_code)

    for idx, row in cat_df.iterrows():
        parent = row.get("Parent Category Code")
        if pd.isna(parent) or not parent or str(parent).strip() == "":
            item_type = str(row.get("Item Type"))
            if item_type == "FINISHED_GOODS":
                cat_df.at[idx, "Parent Category Code"] = "FG"
            elif item_type == "RAW_MATERIAL":
                cat_df.at[idx, "Parent Category Code"] = "RM"
            elif item_type == "PACKAGING_MATERIAL":
                cat_df.at[idx, "Parent Category Code"] = "PKG"
            elif item_type == "CONSUMABLES":
                cat_df.at[idx, "Parent Category Code"] = "CON"
            elif item_type == "ASSETS":
                cat_df.at[idx, "Parent Category Code"] = "AST"
            else:
                cat_df.at[idx, "Parent Category Code"] = "RM"
                
    items_df = sheets.get("Inventory_Items", pd.DataFrame())
    if not items_df.empty:
        # Sanitize missing category code
        for idx, row in items_df.iterrows():
            if pd.isna(row.get("Category Code")) or str(row.get("Category Code")).strip() == "":
                items_df.at[idx, "Category Code"] = "FG" if row.get("Item Type") == "FINISHED_GOODS" else "RM"
                
    bom_df = sheets.get("BOM", pd.DataFrame())
    if not bom_df.empty:
        # Fix column mismatch for BOMImporter
        if "Component Item Code" in bom_df.columns:
            bom_df.rename(columns={"Component Item Code": "Component SKU"}, inplace=True)
                
    # Dataset A: RM_MASTER_CERTIFICATION_DATA
    rm_writer = pd.ExcelWriter(os.path.join(OUT_DIR, "RM_MASTER_CERTIFICATION_DATA.xlsx"))
    
    if "Instructions" in sheets:
        sheets["Instructions"].to_excel(rm_writer, index=False, sheet_name="Instructions")
    if "UoM" in sheets:
        sheets["UoM"].to_excel(rm_writer, index=False, sheet_name="UoM")
    if "Suppliers" in sheets:
        sheets["Suppliers"].to_excel(rm_writer, index=False, sheet_name="Suppliers")
        
    rm_cat_df = cat_df[cat_df["Category Code"].isin(rm_cats)]
    rm_cat_df.to_excel(rm_writer, index=False, sheet_name="Inventory_Categories")
    
    attr_df = sheets.get("Category_Attributes", pd.DataFrame())
    if not attr_df.empty:
        rm_attr_df = attr_df[attr_df["Category Code"].isin(rm_cats)]
        rm_attr_df.to_excel(rm_writer, index=False, sheet_name="Category_Attributes")
        
    if not items_df.empty:
        rm_items_df = items_df[~items_df["Item Type"].isin(["FINISHED_GOODS"])]
        rm_items_df.to_excel(rm_writer, index=False, sheet_name="Inventory_Items")
        
    if not bom_df.empty:
        bom_df.to_excel(rm_writer, index=False, sheet_name="BOM")
        
    rm_writer.close()
    
    # Dataset B: FG_BOUNDARY_CERTIFICATION_DATA
    fg_writer = pd.ExcelWriter(os.path.join(OUT_DIR, "FG_BOUNDARY_CERTIFICATION_DATA.xlsx"))
    fg_cat_df = cat_df[cat_df["Category Code"].isin(fg_cats)]
    fg_cat_df.to_excel(fg_writer, index=False, sheet_name="Inventory_Categories")
    
    if not attr_df.empty:
        fg_attr_df = attr_df[attr_df["Category Code"].isin(fg_cats)]
        fg_attr_df.to_excel(fg_writer, index=False, sheet_name="Category_Attributes")
        
    if not items_df.empty:
        fg_items_df = items_df[items_df["Item Type"] == "FINISHED_GOODS"]
        fg_items_df.to_excel(fg_writer, index=False, sheet_name="Inventory_Items")
        
    fg_writer.close()
    
    # Dataset C: FG_REFERENCE_CERTIFICATION_DATA
    fg_ref_writer = pd.ExcelWriter(os.path.join(OUT_DIR, "FG_REFERENCE_CERTIFICATION_DATA.xlsx"))
    if not items_df.empty:
        fg_items_df = items_df[items_df["Item Type"] == "FINISHED_GOODS"]
        keep_cols = ["Item Code", "Item Name", "Item Type", "Category Code", "Base UoM Code", "Status"]
        ref_df = fg_items_df[[c for c in keep_cols if c in fg_items_df.columns]]
        ref_df.to_excel(fg_ref_writer, index=False, sheet_name="Inventory_Items")
    fg_ref_writer.close()
    
    print("Test datasets successfully generated in tests/data/")

if __name__ == "__main__":
    main()
