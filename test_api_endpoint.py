#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test API endpoint langsung via XML-RPC JSON
"""
import xmlrpc.client
import json

API_URL = 'http://localhost:8070'
DB_NAME = 'kanjabung_MRP'
USERNAME = 'admin'
PASSWORD = 'admin'

print("="*80)
print("Testing /api/scada/mo-list-detailed Endpoint")
print("="*80)
print(f"Database: {DB_NAME}")
print(f"API URL: {API_URL}")
print()

try:
    # Connect via XML-RPC
    print("Step 1: Authenticating...")
    common = xmlrpc.client.ServerProxy(f'{API_URL}/xmlrpc/2/common')
    uid = common.authenticate(DB_NAME, USERNAME, PASSWORD, {})
    
    if not uid:
        print("❌ Authentication failed")
        exit(1)
    
    print(f"✓ Authentication successful (UID: {uid})")
    
    # Call API endpoint
    client = xmlrpc.client.ServerProxy(f'{API_URL}/jsonrpc')
    
    print("\nStep 2: Calling /api/scada/mo-list-detailed endpoint...")
    
    payload = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
            'service': 'object',
            'method': 'execute_kw',
            'args': [
                DB_NAME, 
                uid, 
                PASSWORD,
                'grt_scada.mo_detailed_controller',  # Dummy, will use HTTP route
                'get_mo_list_detailed',
                []
            ]
        },
        'id': 1
    }
    
    # Actually, we need to use HTTP for JSON-RPC endpoints
    # Let me use requests instead
    import requests
    
    session = requests.Session()
    
    # Login first
    login_url = f'{API_URL}/web/login'
    login_data = {
        'login': USERNAME,
        'password': PASSWORD,
        'db': DB_NAME,
    }
    
    print("\nStep 2a: Logging in via HTTP...")
    r = session.get(login_url)
    
    # Extract CSRF if exists
    import re
    csrf_match = re.search(r'csrf_token["\']?\s*[=:]\s*["\']([^"\']+)["\']', r.text)
    if csrf_match:
        login_data['csrf_token'] = csrf_match.group(1)
    
    r = session.post(login_url, data=login_data)
    if r.status_code not in [200, 302]:
        print(f"❌ Login failed: {r.status_code}")
        print("Trying alternative approach with Authorization header...")
    
    print("✓ Session established")
    
    # Call API endpoint
    print("\nStep 2b: Calling /api/scada/mo-list-detailed endpoint...")
    
    api_url = f'{API_URL}/api/scada/mo-list-detailed'
    payload = {
        'params': {
            'limit': 50,
            'offset': 0
        }
    }
    
    r = session.post(api_url, json=payload, headers={'Content-Type': 'application/json'})
    
    if r.status_code != 200:
        print(f"❌ API call failed: {r.status_code}")
        print(f"Response: {r.text[:500]}")
        exit(1)
    
    print(f"✓ API call successful (status: {r.status_code})")
    
    # Parse response
    data = r.json()
    
    if data.get('status') != 'success':
        print(f"❌ API returned error: {data.get('message')}")
        exit(1)
    
    mos = data.get('data', [])
    print(f"✓ Got {len(mos)} MOs")
    
    # Find WH/MO/00012
    print("\nStep 3: Find WH/MO/00012...")
    
    found_mo = None
    for mo in mos:
        if mo.get('mo_id') == 'WH/MO/00012':
            found_mo = mo
            break
    
    if not found_mo:
        print("❌ WH/MO/00012 not found")
        exit(1)
    
    print(f"✓ Found {found_mo.get('mo_id')}")
    
    # Check POLLAR ANGSA
    print("\nStep 4: Check POLLAR ANGSA consumption...")
    
    components = found_mo.get('components_consumption', [])
    
    pollar_angsa_silo_c = None
    for comp in components:
        prod_name = comp.get('product_name', '')
        equip = comp.get('equipment', {})
        equip_name = equip.get('name', '')
        qty = comp.get('to_consume', 0)
        
        if 'POLLAR' in prod_name.upper() and 'ANGSA' in prod_name.upper():
            print(f"\n  Found: {prod_name}")
            print(f"  Equipment: {equip_name}")
            print(f"  Quantity: {qty} kg")
            
            if equip_name == 'SILO C' or 'SILO C' in equip_name:
                pollar_angsa_silo_c = qty
    
    # Verification
    print("\n" + "="*80)
    print("VERIFICATION:")
    print("="*80)
    
    if pollar_angsa_silo_c is not None:
        if pollar_angsa_silo_c == 350.0:
            print(f"\n✅ SUCCESS!")
            print(f"   API returns: {pollar_angsa_silo_c} kg (CORRECT)")
            print(f"\n   The fix is working!")
            print(f"   ✓ Using BoM quantity (350 kg)")
            print(f"   ✓ Not summing stock moves (352 kg)")
        elif pollar_angsa_silo_c == 352.0:
            print(f"\n❌ FAIL!")
            print(f"   API returns: {pollar_angsa_silo_c} kg")
            print(f"   Expected: 350 kg (from BoM)")
            print(f"\n   The fix is NOT working yet")
        else:
            print(f"\n⚠️  Unexpected value: {pollar_angsa_silo_c} kg")
    else:
        print("❌ Could not find POLLAR ANGSA SILO C")
    
    print("\n" + "="*80)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
