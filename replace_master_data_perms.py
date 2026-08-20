import os
import glob

# Mapping of old permissions to new AaramIdentity permissions
mapping = {
    "CAN_IMPORT_MASTER_DATA": "MASTER_DATA_IMPORT",
    "CAN_EXPORT_MASTER_DATA": "MASTER_DATA_EXPORT",
    "CAN_VIEW_MASTER_DATA_HISTORY": "MASTER_DATA_ACTIVITY_VIEW"
}

files = glob.glob("/Users/sumatidhingra/Documents/AaramBooks/Aaram_Inventory/frontend/src/**/*.tsx", recursive=True)

for file in files:
    with open(file, 'r') as f:
        content = f.read()
    
    new_content = content
    for old, new in mapping.items():
        new_content = new_content.replace(old, new)
        
    if content != new_content:
        with open(file, 'w') as f:
            f.write(new_content)
        print(f"Updated {file}")

print("Done")
