import os
import re

def build_file_map(root_dir):
    file_map = {}
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            if f.endswith(('.ts', '.tsx', '.js', '.jsx', '.css')):
                rel_dir = os.path.relpath(dirpath, root_dir)
                if rel_dir == '.':
                    rel_dir = ''
                full_path = os.path.normpath(os.path.join(rel_dir, f))
                file_map[full_path.lower()] = full_path
    return file_map

def check_imports():
    root = 'frontend/src'
    file_map = build_file_map(root)
    import_re = re.compile(r'from\s+[\'"]([^\'"]+)[\'"]')
    
    errors = 0
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if not f.endswith(('.ts', '.tsx')): continue
            filepath = os.path.join(dirpath, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                
                for match in import_re.finditer(content):
                    imp = match.group(1)
                    if not imp.startswith('.'): continue
                    
                    # Resolve import relative to current file
                    rel_dir = os.path.relpath(dirpath, root)
                    if rel_dir == '.': rel_dir = ''
                    
                    resolved = os.path.normpath(os.path.join(rel_dir, imp))
                    # Handle index imports
                    if os.path.basename(resolved).find('.') == -1:
                        # Try to find exactly what it matched
                        pass
                        
