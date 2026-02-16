#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Upgrade module grt_scada setelah Odoo restart
"""

import xmlrpc.client
import time

ODOO_URL = "http://localhost:8070"
ODOO_DB = "manukanjabung"
ODOO_USERNAME = "admin"
ODOO_PASSWORD = "admin"

def main():
    print("=" * 70)
    print("UPGRADE MODULE GRT_SCADA (After Restart)")
    print("=" * 70)
    
    print("\n⏳ Menunggu Odoo siap...")
    
    # Wait for Odoo to be ready
    max_retries = 10
    for i in range(max_retries):
        try:
            common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
            version = common.version()
            print(f"✅ Odoo ready! Version: {version.get('server_version')}")
            break
        except Exception as e:
            if i < max_retries - 1:
                print(f"   Retry {i+1}/{max_retries}... ({e})")
                time.sleep(3)
            else:
                print(f"❌ Odoo tidak ready setelah {max_retries} retries")
                print(f"   Pastikan Odoo sudah berjalan di {ODOO_URL}")
                return
    
    # Authenticate
    try:
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        if not uid:
            print("❌ Gagal autentikasi")
            return
        
        print(f"✅ Authenticated as User ID: {uid}")
        
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        
        # Find module
        module_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.module.module', 'search',
            [[('name', '=', 'grt_scada')]]
        )
        
        if not module_ids:
            print("❌ Module grt_scada tidak ditemukan")
            return
        
        # Upgrade
        print("\n🔄 Upgrading module grt_scada...")
        
        result = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.module.module', 'button_immediate_upgrade',
            [module_ids]
        )
        
        print("✅ Upgrade command sent")
        print("⏳ Waiting for upgrade to complete...")
        time.sleep(10)
        
        print("\n" + "=" * 70)
        print("✅ UPGRADE SELESAI")
        print("=" * 70)
        print("\nTest endpoint dengan:")
        print("    python test_mo_consumption_api.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
