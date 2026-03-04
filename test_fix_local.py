#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test API endpoint untuk memverifikasi fix
Database: kanjabung_MRP (local copy)
Target: Check WH/MO/00012 POLLAR ANGSA SILO C апakah 350 (fix) atau 352 (belum)
"""
import requests
import json

# Configuration
API_URL = 'http://localhost:8070'
DB_NAME = 'kanjabung_MRP'
USERNAME = 'admin'
PASSWORD = 'admin'

print("="*80)
print("Testing API Fix: Equipment-based Grouping")
print("="*80)
print(f"Database: {DB_NAME}")
print(f"API URL: {API_URL}")
print()

# Step 1: Get authentication token/session
session = requests.Session()

# First, get the login page to extract CSRF token
login_page_url = f'{API_URL}/web/login'
print("Step 1: Getting CSRF token...")
response = session.get(login_page_url)
if response.status_code != 200:
    print(f"⚠️  Could not get login page: {response.status_code}")
else:
    # Try to extract CSRF token from HTML
    import re
    csrf_match = re.search(r'csrf_token["\']?\s*[=:]\s*["\']([^"\']+)["\']', response.text)
    csrf_token = csrf_match.group(1) if csrf_match else None

print("Step 1: Authenticating...")
login_data = {
    'login': USERNAME,
    'password': PASSWORD,
    'db': DB_NAME,
}

# Add CSRF token if found
if csrf_token:
    login_data['csrf_token'] = csrf_token

response = session.post(login_page_url, data=login_data)
if response.status_code not in [200, 302]:
    print(f"❌ Login failed: {response.status_code}")
    print(response.text[:500])
    exit(1)

print("✓ Authentication successful")

# Step 2: Call API endpoint
print("\nStep 2: Calling /api/scada/mo-list-detailed...")

api_endpoint = f'{API_URL}/api/scada/mo-list-detailed'
headers = {
    'Content-Type': 'application/json',
}

payload = {
    'params': {
        'limit': 50,
        'offset': 0
    }
}

response = session.post(api_endpoint, json=payload, headers=headers)

if response.status_code != 200:
    print(f"❌ API call failed: {response.status_code}")
    print(response.text)
    exit(1)

print("✓ API call successful")

# Step 3: Parse and analyze response
print("\nStep 3: Analyzing response...")

data = response.json()

if data.get('status') != 'success':
    print(f"❌ API returned error: {data.get('message')}")
    exit(1)

mos = data.get('data', [])
print(f"Found {len(mos)} Manufacturing Orders")

# Find WH/MO/00012
print("\n" + "="*80)
print("Searching for WH/MO/00012...")
print("="*80)

found_mo = None
for mo in mos:
    if mo.get('mo_id') == 'WH/MO/00012':
        found_mo = mo
        break

if not found_mo:
    print("\n⚠️  WH/MO/00012 not found in response")
    print(f"\nFirst few MOs in database:")
    for mo in mos[:5]:
        print(f"  - {mo.get('mo_id')}: {mo.get('product_name')} (state: {mo.get('state')})")
    exit(1)

print(f"\n✅ Found MO: {found_mo.get('mo_id')}")
print(f"   Product: {found_mo.get('product_name')}")
print(f"   State: {found_mo.get('state')}")
print(f"   Quantity: {found_mo.get('quantity')} kg")

# Step 4: Check components consumption
print("\n" + "="*80)
print("Component Consumption Details:")
print("="*80)

components = found_mo.get('components_consumption', [])
print(f"\nTotal components: {len(components)}\n")

pollar_angsa_entries = []
for comp in components:
    prod_name = comp.get('product_name', 'Unknown')
    equipment = comp.get('equipment', {})
    equip_name = equipment.get('name', 'No Equipment')
    equip_code = equipment.get('code', 'No Code')
    to_consume = comp.get('to_consume', 0)
    reserved = comp.get('reserved', 0)
    consumed = comp.get('consumed', 0)
    
    print(f"Product: {prod_name}")
    print(f"  Equipment: {equip_name} ({equip_code})")
    print(f"  To Consume: {to_consume} kg")
    print(f"  Reserved: {reserved} kg")
    print(f"  Consumed: {consumed} kg")
    print()
    
    # Track POLLAR ANGSA entries
    if 'POLLAR' in prod_name.upper() or 'ANGSA' in prod_name.upper():
        pollar_angsa_entries.append({
            'product': prod_name,
            'equipment': equip_name,
            'code': equip_code,
            'to_consume': to_consume
        })

# Step 5: Verification
print("="*80)
print("VERIFICATION RESULT:")
print("="*80)

silo_c_entry = None
for entry in pollar_angsa_entries:
    if entry['code'] == 'silo103' or entry['equipment'] == 'SILO C':
        silo_c_entry = entry
        break

if silo_c_entry:
    qty = silo_c_entry['to_consume']
    print(f"\n✓ Found POLLAR ANGSA SILO C (103)")
    print(f"  Quantity: {qty} kg")
    
    if qty == 350.0:
        print(f"\n✅ SUCCESS! API returns 350 kg (CORRECT)")
        print(f"   The fix is working perfectly!")
    elif qty == 352.0:
        print(f"\n❌ FAIL! API still returns 352 kg")
        print(f"   The fix may not have been applied or Odoo needs restart")
    else:
        print(f"\n⚠️  Unexpected value: {qty} kg")
        print(f"   Expected: 350 or 352")
else:
    print("\n⚠️  Could not find POLLAR ANGSA for SILO C")
    print("\nAll POLLAR ANGSA entries found:")
    for entry in pollar_angsa_entries:
        print(f"  - {entry['equipment']} ({entry['code']}): {entry['to_consume']} kg")

print("\n" + "="*80)
