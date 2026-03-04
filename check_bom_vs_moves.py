#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check BoM untuk WH/MO/00012 dan bandingkan dengan stock moves
"""
import xmlrpc.client

API_URL = 'http://localhost:8070'
DB_NAME = 'kanjabung_MRP'
USERNAME = 'admin'
PASSWORD = 'admin'

print("="*80)
print("BOM vs Stock Moves Analysis")
print("="*80)

# Connect
common = xmlrpc.client.ServerProxy(f'{API_URL}/xmlrpc/2/common')
uid = common.authenticate(DB_NAME, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{API_URL}/xmlrpc/2/object')

# Find WH/MO/00012
print("\nStep 1: Get MO Details")
mos = models.execute_kw(DB_NAME, uid, PASSWORD, 'mrp.production', 'search_read',
    [[('name', '=', 'WH/MO/00012')]],
    {'fields': ['id', 'name', 'bom_id', 'product_id', 'product_qty'], 'limit': 1}
)
mo = mos[0]
mo_id = mo['id']
bom_id = mo['bom_id'][0] if mo['bom_id'] else None

print(f"MO: {mo['name']}")
print(f"Product: {mo['product_id'][1]} (Qty: {mo['product_qty']} kg)")
print(f"BoM ID: {mo['bom_id'][1] if mo['bom_id'] else 'None'}")

if not bom_id:
    print("\n❌ No BoM assigned")
    exit(1)

# Get BoM lines
print("\nStep 2: Get BoM Lines")
bom_lines = models.execute_kw(DB_NAME, uid, PASSWORD, 'mrp.bom.line', 'search_read',
    [[('bom_id', '=', bom_id)]],
    {
        'fields': ['product_id', 'product_qty', 'product_uom_id', 'scada_equipment_id'],
        'limit': 100
    }
)

print(f"Found {len(bom_lines)} BoM lines:")
print()

bom_pollar = None
for line in bom_lines:
    prod = line['product_id']
    prod_name = prod[1] if prod else 'Unknown'
    qty = line['product_qty']
    uom = line['product_uom_id'][1] if line['product_uom_id'] else 'Unknown'
    equip = line['scada_equipment_id']
    equip_name = equip[1] if equip else 'No Equipment'
    
    print(f"Product: {prod_name}")
    print(f"  Qty: {qty} {uom}")
    print(f"  Equipment: {equip_name}")
    print()
    
    # Track POLLAR ANGSA
    if 'POLLAR' in prod_name.upper() and 'ANGSA' in prod_name.upper():
        bom_pollar = {
            'product': prod_name,
            'qty': qty,
            'equipment': equip_name
        }

# Compare with stock moves
print("Step 3: Get Stock Moves")
moves = models.execute_kw(DB_NAME, uid, PASSWORD, 'stock.move', 'search_read',
    [[('raw_material_production_id', '=', mo_id)]],
    {
        'fields': ['id', 'product_id', 'product_uom_qty', 'state', 'scada_equipment_id'],
        'limit': 100
    }
)

pollar_moves = [m for m in moves if 'POLLAR' in m['product_id'][1].upper() and 'ANGSA' in m['product_id'][1].upper()]

print(f"Found {len(pollar_moves)} POLLAR ANGSA stock moves:")
print()

total_moves_qty = 0
for idx, move in enumerate(pollar_moves, 1):
    qty = move['product_uom_qty']
    state = move['state']
    equip_name = move['scada_equipment_id'][1] if move['scada_equipment_id'] else 'No Equipment'
    
    print(f"Move #{idx} (ID: {move['id']}): {qty} kg - state: {state} - {equip_name}")
    total_moves_qty += qty

# Analysis
print("\n" + "="*80)
print("ANALYSIS:")
print("="*80)

if bom_pollar:
    print(f"\nBoM Line for POLLAR ANGSA:")
    print(f"  Quantity: {bom_pollar['qty']} kg")
    print(f"  Equipment: {bom_pollar['equipment']}")

print(f"\nTotal Stock Moves for POLLAR ANGSA: {total_moves_qty} kg")

if len(pollar_moves) > 1:
    print(f"\n⚠️  Multiple moves detected!")
    print(f"   BoM expects: {bom_pollar['qty'] if bom_pollar else '?'} kg")
    print(f"   Actual moves: {len(pollar_moves)} moves totaling {total_moves_qty} kg")
    print(f"\n   Possible causes:")
    print(f"   1. MO was modified after creation (quantity changed)")
    print(f"   2. Manual move splitting")
    print(f"   3. Partial reception/return")

print("\nNote: UI displays BoM quantities, API should also group by equipment")
print("="*80)
