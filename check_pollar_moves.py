#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detail check untuk 2 stock moves POLLAR ANGSA di SILO C
"""
import xmlrpc.client

API_URL = 'http://localhost:8070'
DB_NAME = 'kanjabung_MRP'
USERNAME = 'admin'
PASSWORD = 'admin'

print("="*80)
print("Detailed Move Analysis for POLLAR ANGSA")
print("="*80)

# Connect
common = xmlrpc.client.ServerProxy(f'{API_URL}/xmlrpc/2/common')
uid = common.authenticate(DB_NAME, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{API_URL}/xmlrpc/2/object')

# Find WH/MO/00012
mos = models.execute_kw(DB_NAME, uid, PASSWORD, 'mrp.production', 'search_read',
    [[('name', '=', 'WH/MO/00012')]],
    {'fields': ['id'], 'limit': 1}
)
mo_id = mos[0]['id']

# Get moves for POLLAR ANGSA
print("\nFetching all stock moves for WH/MO/00012...")
moves = models.execute_kw(DB_NAME, uid, PASSWORD, 'stock.move', 'search_read',
    [[('raw_material_production_id', '=', mo_id)]],
    {
        'fields': ['id', 'name', 'product_id', 'product_uom_qty', 'reserved_availability', 
                   'quantity_done', 'state', 'scada_equipment_id'],
        'limit': 100
    }
)

# Filter for POLLAR ANGSA
pollar_moves = [m for m in moves if 'POLLAR' in m['product_id'][1].upper() and 'ANGSA' in m['product_id'][1].upper()]

print(f"\nFound {len(pollar_moves)} POLLAR ANGSA moves:")
print()

total_qty = 0
for idx, move in enumerate(pollar_moves, 1):
    move_id = move['id']
    prod_name = move['product_id'][1]
    qty = move['product_uom_qty']
    reserved = move['reserved_availability']
    consumed = move['quantity_done']
    state = move['state']
    equip = move['scada_equipment_id']
    equip_name = equip[1] if equip else 'No Equipment'
    
    print(f"Move #{idx} (ID: {move_id})")
    print(f"  Product: {prod_name}")
    print(f"  To Consume: {qty} kg")
    print(f"  Reserved: {reserved} kg")
    print(f"  Consumed: {consumed} kg")
    print(f"  State: {state}")
    print(f"  Equipment: {equip_name}")
    print()
    
    total_qty += qty

print("="*80)
print(f"TOTALS:")
print(f"  Move count: {len(pollar_moves)}")
print(f"  Total quantity: {total_qty} kg")
print(f"  Expected (from UI screenshot): 350 kg")
print(f"  Difference: {total_qty - 350} kg")
print("="*80)

# Now check if there's any cancellation status
print("\nChecking move states...")
for move in pollar_moves:
    print(f"  Move {move['id']}: state = {move['state']}")

print("\nHypothesis: One of the moves should be CANCELLED or DONE")
print("to match the UI display of 350 kg")
