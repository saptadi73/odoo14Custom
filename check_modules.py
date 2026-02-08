#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check if Odoo modules are detected in addons paths
"""
import os
import sys

# Addons paths from odoo.conf
addons_paths = [
    r'C:\odoo14c\server\odoo\addons',
    r'C:\addon14'
]

def check_modules_in_path(path):
    """Check for valid Odoo modules in a given path"""
    if not os.path.exists(path):
        print(f"❌ Path does not exist: {path}")
        return []
    
    print(f"\n📁 Checking path: {path}")
    modules = []
    
    try:
        items = os.listdir(path)
        for item in items:
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                manifest_path = os.path.join(item_path, '__manifest__.py')
                if os.path.exists(manifest_path):
                    modules.append(item)
        
        print(f"✅ Found {len(modules)} modules")
        if modules and path.endswith('addon14'):
            print(f"\nFirst 10 modules:")
            for mod in sorted(modules)[:10]:
                print(f"  - {mod}")
        
        return modules
    except Exception as e:
        print(f"❌ Error reading path: {e}")
        return []

if __name__ == '__main__':
    print("=" * 60)
    print("Odoo Module Detection Check")
    print("=" * 60)
    
    all_modules = []
    for path in addons_paths:
        modules = check_modules_in_path(path)
        all_modules.extend(modules)
    
    print(f"\n" + "=" * 60)
    print(f"TOTAL MODULES DETECTED: {len(all_modules)}")
    print("=" * 60)
