#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check stock moves for WH/MO/00012 using Odoo Shell
"""
import sys
import os

# Setup Odoo environment
sys.path.insert(0, 'C:\\odoo14c\\server')
import odoo
from odoo import api, SUPERUSER_ID

# Initialize Odoo
# We need to figure out the database name first
print("Available databases:")
odoo.service.db.list_dbs(force=True)

# Try common database names
db_names = ['odoo', 'odoo14', 'postgres', 'scada']
config_file = 'C:\\addon14\\odoo.conf'

# Parse config to get connection details
import configparser
config = configparser.ConfigParser()
config.read(config_file)

print("\nDatabase configuration:")
print(f"  db_host: {config.get('options', 'db_host', fallback='localhost')}")
print(f"  db_port: {config.get('options', 'db_port', fallback='5432')}")
print(f"  db_user: {config.get('options', 'db_user', fallback='odoo')}")

# Use psycopg2 to list databases
import psycopg2

try:
    conn = psycopg2.connect(
        host=config.get('options', 'db_host', fallback='localhost'),
        port=config.get('options', 'db_port', fallback='5432'),
        user=config.get('options', 'db_user', fallback='odoo'),
        password=config.get('options', 'db_password', fallback='odoo'),
        dbname='postgres'  # Connect to postgres db to list all databases
    )
    cursor = conn.cursor()
    cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;")
    databases = cursor.fetchall()
    
    print("\nAvailable databases:")
    for db in databases:
        print(f"  - {db[0]}")
    
    cursor.close()
    conn.close()
    
    # Try to find the most likely database
    likely_db = None
    for db in databases:
        db_name = db[0]
        if db_name in ['odoo14', 'odoo', 'scada', 'grt']:
            likely_db = db_name
            break
    
    if not likely_db and databases:
        # Use first non-system database
        for db in databases:
            if db[0] not in ['postgres', 'template0', 'template1']:
                likely_db = db[0]
                break
    
    if likely_db:
        print(f"\nUsing database: {likely_db}")
        
        # Now connect to Odoo with the database
        odoo.tools.config.parse_config(['--config', config_file, '-d', likely_db])
        with api.Environment.manage():
            registry = odoo.registry(likely_db)
            with registry.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                
                # Find MO
                mo = env['mrp.production'].search([('name', '=', 'WH/MO/00012')], limit=1)
                
                if not mo:
                    print("\n⚠️  MO WH/MO/00012 not found!")
                else:
                    print("\n" + "="*80)
                    print(f"MO: {mo.name}")
                    print(f"Product: {mo.product_id.display_name}")
                    print(f"MO Equipment: {mo.scada_equipment_id.name if mo.scada_equipment_id else 'None'}")
                    print("="*80)
                    
                    # Check raw material moves
                    print("\nRaw Material Moves (move_raw_ids):")
                    print("="*80)
                    
                    from collections import defaultdict
                    product_summary = defaultdict(lambda: {'qty': 0, 'reserved': 0, 'consumed': 0, 'moves': []})
                    
                    for move in mo.move_raw_ids:
                        equipment_name = move.scada_equipment_id.name if move.scada_equipment_id else 'No Equipment'
                        equipment_code = move.scada_equipment_id.equipment_code if move.scada_equipment_id else 'No Code'
                        
                        print(f"\nMove ID: {move.id}")
                        print(f"  Product: {move.product_id.display_name}")
                        print(f"  To Consume: {move.product_uom_qty} {move.product_uom.name}")
                        print(f"  Reserved: {move.reserved_availability}")
                        print(f"  Consumed: {move.quantity_done}")
                        print(f"  State: {move.state}")
                        print(f"  Equipment: {equipment_name} ({equipment_code})")
                        
                        # Group by product
                        product_key = (move.product_id.product_tmpl_id.id, move.product_id.id)
                        product_summary[product_key]['qty'] += move.product_uom_qty
                        product_summary[product_key]['reserved'] += move.reserved_availability
                        product_summary[product_key]['consumed'] += move.quantity_done
                        product_summary[product_key]['moves'].append({
                            'id': move.id,
                            'name': move.product_id.display_name,
                            'qty': move.product_uom_qty,
                            'equipment': f"{equipment_name} ({equipment_code})"
                        })
                    
                    print("\n" + "="*80)
                    print("Summary grouped by Product (as API does):")
                    print("="*80)
                    
                    for product_key, data in product_summary.items():
                        if len(data['moves']) > 1:
                            print(f"\n⚠️  Product has {len(data['moves'])} moves:")
                            print(f"  API will return total: {data['qty']} kg")
                            for m in data['moves']:
                                print(f"    - Move {m['id']}: {m['qty']} kg from {m['equipment']}")
                        else:
                            m = data['moves'][0]
                            print(f"\n✓ {m['name']}: {data['qty']} kg from {m['equipment']}")
                    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
