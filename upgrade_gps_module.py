#!/usr/bin/env python3
import xmlrpc.client

url = 'http://localhost:8070'
db = 'kanjabung_MRP'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
print(f"Authenticated as uid: {uid}")

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Search for module
module_ids = models.execute_kw(db, uid, password,
    'ir.module.module', 'search',
    [[['name', '=', 'grt_crm_business_category']]])

if module_ids:
    print(f"Found module ID: {module_ids[0]}")
    
    # Upgrade module
    result = models.execute_kw(db, uid, password,
        'ir.module.module', 'button_immediate_upgrade',
        [module_ids])
    
    print("Module upgrade initiated successfully")
    print(f"Result: {result}")
else:
    print("Module not found")
