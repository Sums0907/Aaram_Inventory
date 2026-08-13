import sys

def assert_destructive_operation_allowed(operation: str, db_url: str):
    from src.foundation.configuration.settings import get_settings
    settings = get_settings()
    env = settings.DATABASE_ENV.lower()

    if env != "test":
        print("==================================================")
        print("DATABASE SAFETY VIOLATION")
        print("==================================================")
        print(f"Database:\n{db_url}")
        print(f"\nEnvironment:\n{env.upper()}")
        print(f"\nOperation:\n{operation}")
        print("\nRESULT:\nBLOCKED")
        print("\nDestructive database operations are permitted only")
        print("against explicitly classified TEST databases.")
        print("==================================================")
        sys.exit(1)
