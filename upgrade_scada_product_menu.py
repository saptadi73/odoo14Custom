#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Upgrade grt_scada module untuk menambahkan menu Product ID Reference
Version: 7.0.85
"""

import xmlrpc.client
import sys
from datetime import datetime

# Konfigurasi
URL = 'http://localhost:8069'
DB = 'rimang'
USERNAME = 'admin'
PASSWORD = 'admin'
MODULE_NAME = 'grt_scada'

def print_header(title):
    """Print header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def upgrade_module():
    """Upgrade module grt_scada"""
    try:
        print_header(f"UPGRADE MODULE: {MODULE_NAME}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Connecting to Odoo...")
        
        # Authenticate
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        
        if not uid:
            print("❌ ERROR: Authentication failed!")
            return False
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Authenticated as user ID: {uid}")
        
        # Get module ID
        models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Searching for module '{MODULE_NAME}'...")
        module_ids = models.execute_kw(
            DB, uid, PASSWORD,
            'ir.module.module', 'search',
            [[['name', '=', MODULE_NAME]]]
        )
        
        if not module_ids:
            print(f"❌ ERROR: Module '{MODULE_NAME}' not found!")
            return False
        
        module_id = module_ids[0]
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Found module ID: {module_id}")
        
        # Get module info
        module = models.execute_kw(
            DB, uid, PASSWORD,
            'ir.module.module', 'read',
            [module_id],
            {'fields': ['name', 'state', 'installed_version']}
        )[0]
        
        print(f"\nModule Info:")
        print(f"  Name: {module['name']}")
        print(f"  State: {module['state']}")
        print(f"  Installed Version: {module.get('installed_version', 'N/A')}")
        
        if module['state'] != 'installed':
            print(f"\n❌ ERROR: Module is not in 'installed' state (current: {module['state']})")
            return False
        
        # Upgrade module
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting module upgrade...")
        try:
            models.execute_kw(
                DB, uid, PASSWORD,
                'ir.module.module', 'button_immediate_upgrade',
                [[module_id]]
            )
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Module upgrade initiated successfully!")
            
            print("\n" + "=" * 80)
            print("✅ UPGRADE COMPLETE!")
            print("=" * 80)
            print("\nNEXT STEPS:")
            print("1. Wait for Odoo to restart (if configured)")
            print("2. Refresh your browser (Ctrl+F5)")
            print("3. Access menu: Inventory > Products > Product ID Reference (SCADA)")
            print("4. Check the new view with product_id and product_tmpl_id columns")
            print("\nMenu location:")
            print("  Inventory > Products > Product ID Reference (SCADA)")
            print("=" * 80 + "\n")
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            if 'Registry changed' in error_msg or 'restart' in error_msg.lower():
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Odoo is restarting...")
                print("This is normal. Wait a few seconds and check the menu.")
                return True
            else:
                raise
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print_header("UPGRADE GRT SCADA - Add Product ID Reference Menu")
    print("\nChanges in version 7.0.85:")
    print("  • Added dedicated tree view for product_id and product_tmpl_id")
    print("  • Added search view with category and type filters")
    print("  • Added menu under Inventory > Products")
    print("  • Default filter: active + stockable products")
    print("  • Read-only view for safety")
    
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nUpgrade cancelled.")
        sys.exit(0)
    
    success = upgrade_module()
    
    if success:
        print("\n✅ Done! Module upgraded successfully.")
        sys.exit(0)
    else:
        print("\n❌ Upgrade failed. Please check the errors above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
