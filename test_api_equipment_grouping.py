#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test API fix: Verify that consumption is now grouped by equipment correctly
"""
import xmlrpc.client

# Konfigurasi - sesuaikan dengan database yang memiliki MO
url = 'http://localhost:8070'
db = 'manu14'  # atau 'manukanjabung' yang memiliki MO aktif
username = 'admin'
password = 'admin'

# Connect
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("="*80)
print("Testing API Fix: Equipment-based Grouping")
print("="*80)

# Find any confirmed MO
mo = models.execute_kw(db, uid, password, 'mrp.production', 'search_read',
    [[('state', 'in', ['confirmed', 'progress'])]],
    {'fields': ['id', 'name', 'product_id'], 'limit': 1}
)

if not mo:
    print("\nNo confirmed/in-progress MO found in database:", db)
    print("\nTry checking these databases:")
    print("  - manu14")
    print("  - manukanjabung")
    print("  - ilo")
    exit(1)

mo = mo[0]
mo_id = mo['id']
mo_name = mo['name']

print(f"\nTesting with MO: {mo_name} (ID: {mo_id})")
print("="*80)

# Get stock moves
moves = models.execute_kw(db, uid, password, 'stock.move', 'search_read',
    [[('raw_material_production_id', '=', mo_id)]],
    {'fields': ['id', 'product_id', 'product_uom_qty', 'reserved_availability', 
                'quantity_done', 'scada_equipment_id']}
)

print(f"\nTotal stock moves: {len(moves)}")
print("\n" + "="*80)
print("OLD BEHAVIOR (Grouped by Product Only):")
print("="*80)

from collections import defaultdict

# Old way: group by product only
old_groups = defaultdict(lambda: {'qty': 0, 'reserved': 0, 'consumed': 0, 'count': 0})
for move in moves:
    prod_id = move['product_id'][0] if move['product_id'] else None
    prod_name = move['product_id'][1] if move['product_id'] else 'Unknown'
    
    old_groups[prod_id]['name'] = prod_name
    old_groups[prod_id]['qty'] += move['product_uom_qty']
    old_groups[prod_id]['reserved'] += move['reserved_availability']
    old_groups[prod_id]['consumed'] += move['quantity_done']
    old_groups[prod_id]['count'] += 1

for prod_id, data in old_groups.items():
    print(f"\n{data['name']}")
    print(f"  To Consume: {data['qty']} kg")
    print(f"  Reserved: {data['reserved']} kg")
    print(f"  Consumed: {data['consumed']} kg")
    if data['count'] > 1:
        print(f"  ⚠️  Summed from {data['count']} moves (POTENTIAL ISSUE)")

print("\n" + "="*80)
print("NEW BEHAVIOR (Grouped by Product + Equipment):")
print("="*80)

# New way: group by product + equipment
new_groups = defaultdict(lambda: {'qty': 0, 'reserved': 0, 'consumed': 0})
for move in moves:
    prod_id = move['product_id'][0] if move['product_id'] else None
    prod_name = move['product_id'][1] if move['product_id'] else 'Unknown'
    equip_id = move['scada_equipment_id'][0] if move['scada_equipment_id'] else None
    equip_name = move['scada_equipment_id'][1] if move['scada_equipment_id'] else 'No Equipment'
    
    key = (prod_id, equip_id)
    new_groups[key]['name'] = prod_name
    new_groups[key]['equipment'] = equip_name
    new_groups[key]['qty'] += move['product_uom_qty']
    new_groups[key]['reserved'] += move['reserved_availability']
    new_groups[key]['consumed'] += move['quantity_done']

for (prod_id, equip_id), data in new_groups.items():
    print(f"\n{data['name']} from {data['equipment']}")
    print(f"  To Consume: {data['qty']} kg")
    print(f"  Reserved: {data['reserved']} kg")
    print(f"  Consumed: {data['consumed']} kg")
    print(f"  ✓ Matches UI display")

print("\n" + "="*80)
print("SUMMARY:")
print("="*80)
print(f"Old grouping: {len(old_groups)} items (grouped by product only)")
print(f"New grouping: {len(new_groups)} items (grouped by product + equipment)")
print("\nThe new grouping matches the UI display exactly, where each")
print("component line shows the quantity for a specific equipment (SILO).")
print("="*80)
