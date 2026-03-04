#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check if grt_scada module is installed and loaded
"""
import xmlrpc.client

URL = 'http://localhost:8070'
DB = 'kanjabung_MRP'
USER = 'admin'
PASSWD = 'admin'

try:
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(URL))
    uid = common.authenticate(DB, USER, PASSWD, {})
    
    if not uid:
        print(f"❌ Authentication failed for user: {USER}")
        exit(1)
    
    print(f"✓ Authenticated as user: {USER} (uid={uid})")
    
    # Check if grt_scada module is installed
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(URL))
    
    result = models.execute_kw(DB, uid, PASSWD, 'ir.module.module', 'search_read', 
        [[('name', '=', 'grt_scada')]], 
        {'fields': ['name', 'state', 'installed_version']})
    
    if result:
        module = result[0]
        print(f"\n✓ Module found:")
        print(f"  Name: {module.get('name')}")
        print(f"  State: {module.get('state')}")
        print(f"  Version: {module.get('installed_version')}")
        
        if module.get('state') == 'installed':
            print(f"\n✅ Module IS INSTALLED")
            
            # Check if route is registered
            print(f"\nRouter info:")
            
            # Try to get controller info
            cr = models.execute_kw(DB, uid, PASSWD, 'ir.http', 'search_read',
                [[('module', '=', 'grt_scada')]],
                {'fields': ['module']})
            
            if cr:
                print(f"  HTTP handler entries: {len(cr)}")
            else:
                print(f"  No explicit HTTP entries found")
        else:
            print(f"\n❌ Module is NOT installed, current state: {module.get('state')}")
    else:
        print(f"❌ Module grt_scada not found in database")
        
        # List all installed modules to check what is installed
        print(f"\nSearching for 'scada' in module names...")
        result = models.execute_kw(DB, uid, PASSWD, 'ir.module.module', 'search_read',
            [[('name', 'ilike', 'scada'), ('state', '=', 'installed')]],
            {'fields': ['name', 'state'], 'limit': 20})
        
        if result:
            print(f"Found {len(result)} modules with 'scada':")
            for mod in result:
                print(f"  - {mod['name']} ({mod['state']})")
        else:
            print(f"No modules with 'scada' found")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
