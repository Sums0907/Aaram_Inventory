import os
import re

api_dir = '/Users/sumatidhingra/Documents/AaramBooks/Aaram_Inventory/frontend/src/api'

files_to_fix = [
    'masters.ts',
    'matching.ts',
    'accounting.ts',
    'inventory.ts'
]

for file in files_to_fix:
    filepath = os.path.join(api_dir, file)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Remove hardcoded TOKEN definition
        content = re.sub(r'const\s+TOKEN\s*=\s*"[^"]+";\s*', '', content)
        
        # Remove headers parameter from apiClient calls
        content = re.sub(r',\s*\{\s*headers:\s*\{\s*Authorization:\s*`Bearer\s*\$\{TOKEN\}`\s*\}\s*\}', '', content)
        
        with open(filepath, 'w') as f:
            f.write(content)
            
print("Fixed hardcoded tokens.")
