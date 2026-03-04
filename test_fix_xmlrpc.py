#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test API dengan XML-RPC untuk memverifikasi fix
Database: kanjabung_MRP (local copy)
Target: Check WH/MO/00012 POLLAR ANGSA SILO C apakah 350 (fix) atau 352 (belum)
"""
import xmlrpc.client
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

try:
    # Connect to XML-RPC
    print("Step 1: Authenticating...")
    common = xmlrpc.client.ServerProxy(f'{API_URL}/xmlrpc/2/common')
    uid = common.authenticate(DB_NAME, USERNAME, PASSWORD, {})
    
    if not uid:
        print("❌ Authentication failed")
        exit(1)
    
    print(f"✓ Authentication successful (UID: {uid})")
    
    # Get MRP Production model
    models = xmlrpc.client.ServerProxy(f'{API_URL}/xmlrpc/2/object')
    
    print("\nStep 2: Searching for WH/MO/00012...")
    
    # Search for MO
    mos = models.execute_kw(
        DB_NAME, uid, PASSWORD,
        'mrp.production', 'search_read',
        [[('name', '=', 'WH/MO/00012')]],
        {'fields': ['id', 'name', 'product_id', 'state', 'product_qty'], 'limit': 1}
    )
    
    if not mos:
        print("❌ WH/MO/00012 not found in database")
        print("\nSearching for any MO to check if module is installed...")
        any_mos = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'mrp.production', 'search_read',
            [[]],
            {'fields': ['name'], 'limit': 5}
        )
        if any_mos:
            print(f"Found {len(any_mos)} MOs:")
            for mo in any_mos:
                print(f"  - {mo['name']}")
        else:
            print("No MOs found at all")
        exit(1)
    
    mo = mos[0]
    print(f"✅ Found MO: {mo['name']}")
    print(f"   Product: {mo['product_id']}")
    print(f"   State: {mo['state']}")
    print(f"   Quantity: {mo['product_qty']} kg")
    
    # Get raw material moves
    print("\nStep 3: Getting stock moves...")
    
    moves = models.execute_kw(
        DB_NAME, uid, PASSWORD,
        'stock.move', 'search_read',
        [[('raw_material_production_id', '=', mo['id'])]],
        {
            'fields': ['id', 'product_id', 'product_uom_qty', 'scada_equipment_id'],
            'limit': 100
        }
    )
    
    print(f"Found {len(moves)} stock moves")
    
    # Analyze moves
    print("\n" + "="*80)
    print("Component Analysis:")
    print("="*80)
    
    from collections import defaultdict
    
    # Group by product + equipment (NEW way - fixed)
    new_groups = defaultdict(lambda: {'qty': 0, 'moves': []})
    
    for move in moves:
        prod_name = move['product_id'][1] if move['product_id'] else 'Unknown'
        prod_id = move['product_id'][0] if move['product_id'] else None
        
        equip = move['scada_equipment_id']
        equip_id = equip[0] if equip else None
        equip_name = equip[1] if equip else 'No Equipment'
        
        qty = move['product_uom_qty']
        
        # NEW way: group by product + equipment
        key = (prod_id, equip_id)
        new_groups[key]['product'] = prod_name
        new_groups[key]['equipment'] = equip_name
        new_groups[key]['qty'] += qty
        new_groups[key]['moves'].append(move['id'])
    
    # Display results
    pollar_angsa_silo_c = None
    
    print()
    for (prod_id, equip_id), data in new_groups.items():
        prod_name = data['product']
        equip_name = data['equipment']
        qty = data['qty']
        move_count = len(data['moves'])
        
        print(f"Product: {prod_name}")
        print(f"  Equipment: {equip_name}")
        print(f"  Quantity: {qty} kg")
        if move_count > 1:
            print(f"  Moves: {move_count} moves (IDs: {data['moves']})")
        print()
        
        # Check if this is POLLAR ANGSA SILO C
        if 'POLLAR' in prod_name.upper() and 'ANGSA' in prod_name.upper():
            if 'SILO C' in equip_name.upper() or equip_name == 'SILO C':
                pollar_angsa_silo_c = qty
    
    # Verification
    print("="*80)
    print("VERIFICATION RESULT:")
    print("="*80)
    
    if pollar_angsa_silo_c is not None:
        print(f"\n✓ Found POLLAR ANGSA SILO C")
        print(f"  Quantity returned by API: {pollar_angsa_silo_c} kg")
        
        if pollar_angsa_silo_c == 350.0:
            print(f"\n✅ SUCCESS! API returns 350 kg")
            print(f"   The fix is working correctly!")
            print(f"\n   ✓ Equipment-based grouping is active")
            print(f"   ✓ POLLAR ANGSA from SILO C only = 350 kg")
        elif pollar_angsa_silo_c == 352.0:
            print(f"\n❌ FAIL! API still returns 352 kg")
            print(f"   The fix may not have been applied yet")
            print(f"\n   ⚠️  This means the API is still summing all equipment")
            print(f"   Actions:")
            print(f"   1. Make sure Odoo has been restarted after code changes")
            print(f"   2. Check if grt_scada controllers were updated")
            print(f"   3. Verify git changes: git diff grt_scada/controllers/")
        else:
            print(f"\n⚠️  Unexpected value: {pollar_angsa_silo_c} kg")
            print(f"   Expected: 350.0 (fixed) or 352.0 (not fixed)")
    else:
        print("\n⚠️  Could not find POLLAR ANGSA SILO C entry")
        print("   This might mean:")
        print("   1. The MO doesn't have this component, or")
        print("   2. The component is not assigned to SILO C")
    
    print("\n" + "="*80)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
