#!/usr/bin/env python3
# Verifikasi perbaikan SCSS

import os

print("="*70)
print("VERIFIKASI PERBAIKAN SCSS")
print("="*70)

files_to_check = [
    {
        'name': 'account_dynamic_reports',
        'scss': r'c:\addon14\account_dynamic_reports\static\src\scss\dynamic_common_style.scss',
        'assets_xml': r'c:\addon14\account_dynamic_reports\views\assets.xml',
        'manifest': r'c:\addon14\account_dynamic_reports\__manifest__.py'
    },
    {
        'name': 'om_account_asset',
        'scss': r'c:\addon14\om_account_asset\static\src\scss\account_asset.scss',
        'assets_xml': r'c:\addon14\om_account_asset\views\assets.xml',
        'manifest': r'c:\addon14\om_account_asset\__manifest__.py'
    }
]

all_ok = True

for module in files_to_check:
    print(f"\n{module['name']}")
    print("-" * 70)
    
    # Check SCSS file exists
    if os.path.exists(module['scss']):
        print(f"  ✓ SCSS file exists: {os.path.basename(module['scss'])}")
    else:
        print(f"  ✗ SCSS file NOT found!")
        all_ok = False
    
    # Check assets.xml exists
    if os.path.exists(module['assets_xml']):
        print(f"  ✓ assets.xml exists")
        
        # Check content
        with open(module['assets_xml'], 'r', encoding='utf-8') as f:
            content = f.read()
            if 'assets_backend' in content and '.scss' in content:
                print(f"  ✓ assets.xml correctly references SCSS file")
            else:
                print(f"  ⚠ assets.xml may not be configured correctly")
                all_ok = False
    else:
        print(f"  ✗ assets.xml NOT found!")
        all_ok = False
    
    # Check manifest includes assets.xml
    if os.path.exists(module['manifest']):
        with open(module['manifest'], 'r', encoding='utf-8') as f:
            content = f.read()
            if 'views/assets.xml' in content:
                print(f"  ✓ Manifest includes assets.xml in 'data'")
            else:
                print(f"  ⚠ Manifest does NOT include assets.xml")
                all_ok = False
            
            if "'assets': {" in content:
                print(f"  ⚠ WARNING: Manifest still has 'assets' dict (should be removed for Odoo 14)")
                all_ok = False

print("\n" + "="*70)
if all_ok:
    print("✓ ALL CHECKS PASSED!")
    print("\nRestart Odoo dan error SCSS tidak akan muncul lagi.")
else:
    print("⚠ SOME ISSUES FOUND - Please review above")
print("="*70)
