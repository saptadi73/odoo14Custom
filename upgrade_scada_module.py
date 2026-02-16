#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Upgrade module grt_scada untuk refresh routes
"""

import xmlrpc.client
import time

# Konfigurasi Odoo
ODOO_URL = "http://localhost:8070"
ODOO_DB = "manukanjabung"
ODOO_USERNAME = "admin"
ODOO_PASSWORD = "admin"

def upgrade_module(module_name):
    """Upgrade specific module"""
    print("=" * 70)
    print(f"UPGRADE MODULE: {module_name}")
    print("=" * 70)
    
    try:
        # Connect
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        
        if not uid:
            print("❌ Gagal autentikasi")
            return False
        
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        print(f"✅ Terkoneksi sebagai User ID: {uid}\n")
        
        # Find module
        module_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.module.module', 'search',
            [[('name', '=', module_name)]]
        )
        
        if not module_ids:
            print(f"❌ Module {module_name} tidak ditemukan")
            return False
        
        module_id = module_ids[0]
        
        # Check current state
        module = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.module.module', 'read',
            [[module_id]],
            {'fields': ['name', 'state', 'latest_version']}
        )[0]
        
        print(f"📦 Module: {module['name']}")
        print(f"   State: {module['state']}")
        print(f"   Version: {module.get('latest_version', 'N/A')}")
        
        if module['state'] != 'installed':
            print(f"\n❌ Module tidak dalam state 'installed', tidak bisa upgrade")
            return False
        
        # Upgrade module
        print(f"\n🔄 Upgrading module...")
        
        result = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.module.module', 'button_immediate_upgrade',
            [[module_id]]
        )
        
        print(f"✅ Upgrade command sent")
        print(f"   Result: {result}")
        
        # Wait a bit
        print(f"\n⏳ Waiting 5 seconds for upgrade to complete...")
        time.sleep(5)
        
        # Check new state
        module_after = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.module.module', 'read',
            [[module_id]],
            {'fields': ['name', 'state', 'latest_version']}
        )[0]
        
        print(f"\n📦 Module after upgrade:")
        print(f"   State: {module_after['state']}")
        print(f"   Version: {module_after.get('latest_version', 'N/A')}")
        
        if module_after['state'] == 'installed':
            print(f"\n✅ MODULE BERHASIL DI-UPGRADE")
            return True
        else:
            print(f"\n⚠️  Module state: {module_after['state']}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 70)
    print("UPGRADE MODULE GRT_SCADA")
    print("=" * 70)
    print()
    print("Module ini akan di-upgrade untuk:")
    print("- Refresh routes dan controllers")
    print("- Update model definitions")
    print("- Re-load configurations")
    print()
    
    confirm = input("Lanjutkan upgrade? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Dibatalkan")
        return
    
    success = upgrade_module('grt_scada')
    
    if success:
        print("\n" + "=" * 70)
        print("✅ UPGRADE SELESAI")
        print("=" * 70)
        print()
        print("Silakan test endpoint lagi dengan:")
        print("    python test_mo_consumption_api.py")
    else:
        print("\n" + "=" * 70)
        print("❌ UPGRADE GAGAL")
        print("=" * 70)
        print()
        print("Alternatif: Restart Odoo secara manual")
        print("1. Stop Odoo (Ctrl+C di terminal Odoo)")
        print("2. Start kembali dengan F5 di VS Code Debug")

if __name__ == "__main__":
    main()
