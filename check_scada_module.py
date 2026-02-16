#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check status module grt_scada dan module terkait
"""

import xmlrpc.client

# Konfigurasi Odoo
ODOO_URL = "http://localhost:8070"
ODOO_DB = "manukanjabung"
ODOO_USERNAME = "admin"
ODOO_PASSWORD = "admin"

def check_module(models, uid, module_name):
    """Check status specific module"""
    try:
        module = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.module.module', 'search_read',
            [[('name', '=', module_name)]],
            {'fields': ['name', 'state', 'summary', 'latest_version']}
        )
        
        if module:
            return module[0]
        else:
            return None
    except Exception as e:
        return {'error': str(e)}

def main():
    print("=" * 70)
    print("CHECK MODULE GRT_SCADA")
    print("=" * 70)
    
    try:
        # Connect
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        
        if not uid:
            print("❌ Gagal autentikasi")
            return
        
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        print(f"✅ Terkoneksi sebagai User ID: {uid}\n")
        
        # Check modules
        modules_to_check = [
            'grt_scada',
            'grt_scada_failure_report',
            'mrp',
            'stock',
        ]
        
        for module_name in modules_to_check:
            print(f"Checking module: {module_name}")
            module = check_module(models, uid, module_name)
            
            if module:
                if 'error' in module:
                    print(f"   ❌ Error: {module['error']}\n")
                else:
                    state = module.get('state', 'unknown')
                    if state == 'installed':
                        icon = "✅"
                    elif state == 'uninstalled':
                        icon = "⬜"
                    elif state == 'to upgrade':
                        icon = "⚠️ "
                    elif state == 'to install':
                        icon = "🔄"
                    else:
                        icon = "❓"
                    
                    print(f"   {icon} State: {state}")
                    print(f"   Version: {module.get('latest_version', 'N/A')}")
                    if module.get('summary'):
                        print(f"   Summary: {module.get('summary')}")
                    print()
            else:
                print(f"   ❌ Module not found\n")
        
        # Check if grt_scada routes are registered
        print("\n" + "=" * 70)
        print("CHECK ROUTES")
        print("=" * 70)
        
        # Try to get list of routes (if possible)
        try:
            routes = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'ir.http', 'search_read',
                [[]],
                {'limit': 5}
            )
            print(f"Found {len(routes)} routes registered")
        except Exception as e:
            print(f"Cannot check routes: {e}")
        
        # Check if scada.equipment model exists
        print("\n" + "=" * 70)
        print("CHECK MODELS")
        print("=" * 70)
        
        models_to_check = [
            'scada.equipment',
            'scada.equipment.material.log',
            'mrp.production',
            'stock.move',
        ]
        
        for model_name in models_to_check:
            try:
                count = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    model_name, 'search_count',
                    [[]]
                )
                print(f"   ✅ {model_name}: {count} records")
            except Exception as e:
                print(f"   ❌ {model_name}: {str(e)[:100]}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
