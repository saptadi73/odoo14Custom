#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test API endpoint dengan credentials yang diberikan
"""
import requests
import json
from requests.auth import HTTPBasicAuth

API_URL = 'http://localhost:8070'
DB_NAME = 'kanjabung_MRP'
USERNAME = 'admin'
PASSWORD = 'admin'

print("="*80)
print("Testing /api/scada/mo-list-detailed Endpoint")
print("="*80)
print(f"Database: {DB_NAME}")
print(f"API URL: {API_URL}")
print(f"Username: {USERNAME}")
print()

try:
    session = requests.Session()
    
    # Step 1: Get login page and CSRF token
    print("Step 1: Getting CSRF token...")
    login_url = f'{API_URL}/web/login'
    
    r = session.get(login_url)
    
    # Extract CSRF token from HTML
    import re
    csrf_match = re.search(r'csrf_token["\']?\s*[=:]\s*["\']([^"\']+)["\']', r.text)
    csrf_token = csrf_match.group(1) if csrf_match else ''
    
    if csrf_token:
        print(f"✓ Found CSRF token: {csrf_token[:20]}...")
    else:
        print("⚠️  No CSRF token found, trying without it")
    
    # Step 2: Login
    print("\nStep 2: Logging in...")
    login_data = {
        'login': USERNAME,
        'password': PASSWORD,
        'db': DB_NAME,
    }
    
    if csrf_token:
        login_data['csrf_token'] = csrf_token
    
    r = session.post(login_url, data=login_data, allow_redirects=True)
    
    if 'login' in r.url or 'error' in r.text.lower():
        print(f"⚠️  Login may have failed (URL: {r.url})")
        print("   Trying to call API anyway...")
    else:
        print(f"✓ Login successful (redirected to: {r.url})")
    
    # Step 3: Call API endpoint
    print("\nStep 3: Calling /api/scada/mo-list-detailed...")
    
    api_url = f'{API_URL}/api/scada/mo-list-detailed'
    payload = {
        'params': {
            'limit': 50,
            'offset': 0
        }
    }
    
    r = session.post(
        api_url, 
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status Code: {r.status_code}")
    
    if r.status_code != 200:
        print(f"❌ API call failed")
        print(f"Response: {r.text[:1000]}")
        
        # Try with basic auth
        print("\n" + "="*80)
        print("Trying with Basic Authentication...")
        print("="*80)
        
        session2 = requests.Session()
        session2.auth = HTTPBasicAuth(USERNAME, PASSWORD)
        
        r = session2.post(
            api_url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {r.status_code}")
        
        if r.status_code != 200:
            print(f"❌ Still failed")
            print(f"Response: {r.text[:1000]}")
            exit(1)
    
    print(f"✓ API call successful")
    
    # Parse response
    data = r.json()
    
    print(f"\nResponse status: {data.get('status')}")
    
    if data.get('status') != 'success':
        print(f"❌ API returned error: {data.get('message')}")
        exit(1)
    
    mos = data.get('data', [])
    print(f"✓ Got {len(mos)} MOs in response")
    
    # Find WH/MO/00012
    print("\nStep 4: Finding WH/MO/00012...")
    
    found_mo = None
    for mo in mos:
        if mo.get('mo_id') == 'WH/MO/00012':
            found_mo = mo
            break
    
    if not found_mo:
        print("❌ WH/MO/00012 not found in response")
        print(f"Available MOs:")
        for mo in mos[:5]:
            print(f"  - {mo.get('mo_id')}")
        exit(1)
    
    print(f"✓ Found {found_mo.get('mo_id')}")
    print(f"  Product: {found_mo.get('product_name')}")
    print(f"  State: {found_mo.get('state')}")
    
    # Check POLLAR ANGSA
    print("\nStep 5: Analyzing components...")
    
    components = found_mo.get('components_consumption', [])
    print(f"Total components: {len(components)}\n")
    
    pollar_angsa_entries = []
    
    for comp in components:
        prod_name = comp.get('product_name', '')
        equip = comp.get('equipment', {})
        equip_name = equip.get('name', '')
        equip_code = equip.get('code', '')
        qty = comp.get('to_consume', 0)
        
        if 'POLLAR' in prod_name.upper() and 'ANGSA' in prod_name.upper():
            pollar_angsa_entries.append({
                'product': prod_name,
                'equipment': equip_name,
                'code': equip_code,
                'qty': qty
            })
            
            print(f"✓ {prod_name}")
            print(f"  Equipment: {equip_name} ({equip_code})")
            print(f"  Quantity: {qty} kg")
            print()
    
    # Verification
    print("="*80)
    print("VERIFICATION RESULT:")
    print("="*80)
    
    # Find SILO C entry
    silo_c_entry = None
    for entry in pollar_angsa_entries:
        if entry['code'] == 'silo103' or 'SILO C' in entry['equipment']:
            silo_c_entry = entry
            break
    
    if silo_c_entry:
        qty = silo_c_entry['qty']
        print(f"\n✓ Found POLLAR ANGSA SILO C")
        print(f"  Quantity from API: {qty} kg")
        
        if qty == 350.0:
            print(f"\n✅ SUCCESS! API returns 350 kg")
            print(f"   The fix is working correctly!")
            print(f"\n   ✓ Using BoM quantity (350 kg)")
            print(f"   ✓ Not summing stock moves (352 kg)")
        elif qty == 352.0:
            print(f"\n❌ FAIL! API still returns 352 kg")
            print(f"   Expected: 350 kg (from BoM)")
            print(f"\n   The fix may not have been applied")
        else:
            print(f"\n⚠️  Unexpected value: {qty} kg")
            print(f"   Expected: 350.0 or 352.0")
    else:
        print("\n❌ Could not find POLLAR ANGSA SILO C")
        print("\nAll POLLAR ANGSA entries found:")
        for entry in pollar_angsa_entries:
            print(f"  - {entry['equipment']} ({entry['code']}): {entry['qty']} kg")
    
    print("\n" + "="*80)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
