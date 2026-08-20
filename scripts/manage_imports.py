import argparse
import asyncio
import pandas as pd
from typing import Dict, Any

from src.foundation.database.session import Database
from src.foundation.configuration import get_settings

from src.domains.data_ingestion.services.master_data_application_service import MasterDataApplicationService
from src.domains.data_ingestion.services.master_data_application_service import IMPORTERS

# Keys that are deprecated and should warn the operator
_DEPRECATED_KEYS = {
    "CATEGORY":    "OPERATIONAL_CATEGORY",
    "PRODUCT_SKU": "RAW_MATERIAL",
}

async def run_import(entity_type: str, file_path: str, commit: bool, env: str, user_id: str, sheet_name: str = None):
    entity_type = entity_type.upper()
    if entity_type not in IMPORTERS:
        print(f"Error: Unknown entity type '{entity_type}'.")
        print(f"  Allowed: {', '.join(k for k in IMPORTERS if k not in _DEPRECATED_KEYS)}")
        print(f"  Deprecated (still accepted): {', '.join(_DEPRECATED_KEYS)}")
        return

    # Warn operator if using a deprecated key
    if entity_type in _DEPRECATED_KEYS:
        new_key = _DEPRECATED_KEYS[entity_type]
        print(f"[DEPRECATION WARNING] Entity key '{entity_type}' is deprecated. "
              f"Use '{new_key}' instead. The old key will be removed in a future release.")

    try:
        if sheet_name:
            df = pd.read_excel(file_path, sheet_name=sheet_name).fillna("")
        else:
            df = pd.read_excel(file_path).fillna("")
        data = df.to_dict(orient="records")
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return

    settings = get_settings()
    db = Database(
        db_url=settings.DATABASE_URL,
        debug=settings.DEBUG,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW
    )
    async_session_maker = db._session_factory

    async with async_session_maker() as session:
        service = MasterDataApplicationService(session)
        is_dry_run = not commit
        status_label = "DRY_RUN" if is_dry_run else "COMMITTED"
        
        print(f"\n[{status_label}] Starting Import: {entity_type} from {file_path}")
        
        # Execute Import via Application Service
        try:
            result = await service.execute_import(
                domain=entity_type,
                data=data,
                is_dry_run=is_dry_run,
                user_id=user_id,
                file_name=file_path.split("/")[-1],
                env=env
            )
            
            # Print Summary
            print("\n" + "="*40)
            print("IMPORT SUMMARY REPORT")
            print("="*40)
            print(f"Total Records: {result['total_records']}")
            print(f"Created:       {result['created_count']}")
            print(f"Updated:       {result['updated_count']}")
            print(f"Ignored:       {result['ignored_count']}")
            print(f"Failed:        {result['failed_count']}")
            print(f"Ambiguous:     {result['ambiguous_count']}")
            print("="*40)
            
            if result['failed_count'] > 0 or result['ambiguous_count'] > 0:
                print("\nERRORS:")
                for r in result['row_results']:
                    if r['action'] in ["FAILED", "AMBIGUOUS"]:
                        err_str = ", ".join(r['errors'])
                        ident = f" [{r['identifier']}]" if r['identifier'] else ""
                        print(f"  Row {r['row_index']}{ident}: {r['action']} - {err_str}")
            
            if commit:
                print(f"\n[SUCCESS] Transaction committed.")
            else:
                print("\n[DRY RUN] Transaction rolled back successfully.")
                
        except Exception as e:
            if "Commit blocked" in str(e):
                print(f"\n[BLOCKED] {e}")
            else:
                print(f"\n[FATAL] Import failed with unhandled error: {e}")
            raise e

def main():
    parser = argparse.ArgumentParser(description="AaramBooks Master Data Import CLI")
    parser.add_argument(
        "--entity", type=str, required=True,
        help=(
            "Entity type (Raw Material Sub-Engine): "
            "UOM | OPERATIONAL_CATEGORY | SUPPLIER | RAW_MATERIAL | BOM. "
            "Deprecated aliases still accepted: CATEGORY, PRODUCT_SKU."
        )
    )

    parser.add_argument("--file", type=str, required=True, help="Path to the Excel file")
    parser.add_argument("--sheet", type=str, default=None, help="Specific sheet name to read")
    parser.add_argument("--commit", action="store_true", help="Commit the transaction to the database (removes Dry Run mode)")
    parser.add_argument("--env", type=str, default="dev", help="Environment string for audit logs")
    parser.add_argument("--user", type=str, default=None, help="UUID of the executing user")
    
    args = parser.parse_args()
    asyncio.run(run_import(args.entity, args.file, args.commit, args.env, args.user, args.sheet))

if __name__ == "__main__":
    main()
