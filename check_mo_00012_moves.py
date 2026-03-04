#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check stock moves for WH/MO/00012 to understand why API returns 352 instead of 350
"""
import xmlrpc.client

# Konfigurasi
url = 'http://localhost:8070'
db = 'odoo14c'
username = 'admin'
password = 'admin'

# Connect
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("="*80)
print("Checking MO WH/MO/00012 - POLLAR ANGSA consumption")
print("="*80)

# Find MO
mo = models.execute_kw(db, uid, password, 'mrp.production', 'search_read',
    [[('name', '=', 'WH/MO/00012')]],
    {'fields': ['id', 'name', 'product_id', 'scada_equipment_id'], 'limit': 1}
)

if not mo:
    print("MO not found!")
    exit(1)

mo = mo[0]
print(f"\nMO ID: {mo['id']}")
print(f"MO Name: {mo['name']}")
print(f"Product: {mo['product_id']}")
print(f"MO Equipment: {mo['scada_equipment_id']}")

# Find all move_raw_ids for POLLAR ANGSA (product_id might be 40025 based on screenshot)
print("\n" + "="*80)
print("Stock Moves for Raw Materials (move_raw_ids):")
print("="*80)

moves = models.execute_kw(db, uid, password, 'stock.move', 'search_read',
    [[('raw_material_production_id', '=', mo['id'])]],
    {'fields': ['id', 'name', 'product_id', 'product_uom_qty', 'reserved_availability', 
                'quantity_done', 'state', 'scada_equipment_id']}
)

print(f"\nTotal moves found: {len(moves)}")

pollar_angsa_total = 0
for move in moves:
    product_name = move['product_id'][1] if move['product_id'] else 'No Product'
    equipment_name = move['scada_equipment_id'][1] if move['scada_equipment_id'] else 'No Equipment'
    
    print(f"\nMove ID: {move['id']}")
    print(f"  Product: {product_name}")
    print(f"  To Consume (product_uom_qty): {move['product_uom_qty']}")
    print(f"  Reserved: {move['reserved_availability']}")  
    print(f"  Consumed (quantity_done): {move['quantity_done']}")
    print(f"  State: {move['state']}")
    print(f"  Equipment: {equipment_name}")
    
    if 'POLLAR' in product_name.upper() or 'ANGSA' in product_name.upper():
        pollar_angsa_total += move['product_uom_qty']
        print(f"  >>> This is POLLAR ANGSA! Adding {move['product_uom_qty']} to total")

print("\n" + "="*80)
print(f"POLLAR ANGSA Total from API perspective: {pollar_angsa_total}")
print("="*80)

# Check if there are multiple moves for the same product
print("\n" + "="*80)
print("Grouping by Product (like the API does):")
print("="*80)

from collections import defaultdict
product_groups = defaultdict(lambda: {'qty': 0, 'reserved': 0, 'consumed': 0, 'moves': []})

for move in moves:
    product_id = move['product_id'][0] if move['product_id'] else None
    product_name = move['product_id'][1] if move['product_id'] else 'No Product'
    
    if product_id:
        product_groups[product_id]['qty'] += move['product_uom_qty']
        product_groups[product_id]['reserved'] += move['reserved_availability']
        product_groups[product_id]['consumed'] += move['quantity_done']
        product_groups[product_id]['moves'].append({
            'id': move['id'],
            'name': product_name,
            'qty': move['product_uom_qty'],
            'equipment': move['scada_equipment_id'][1] if move['scada_equipment_id'] else 'No Equipment'
        })

for prod_id, data in product_groups.items():
    if len(data['moves']) > 1:
        print(f"\n⚠️  Product ID {prod_id} has {len(data['moves'])} moves:")
        print(f"  Total to_consume: {data['qty']}")
        for m in data['moves']:
            print(f"    - Move {m['id']}: {m['name']} - {m['qty']} kg (Equipment: {m['equipment']})")
