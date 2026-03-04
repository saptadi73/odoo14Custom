#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check stock moves for WH/MO/00012 across databases
"""
import sys
import psycopg2
import configparser

# Parse config to get connection details
config_file = 'C:\\addon14\\odoo.conf'
config = configparser.ConfigParser()
config.read(config_file)

# Connect to PostgreSQL
conn = psycopg2.connect(
    host=config.get('options', 'db_host', fallback='localhost'),
    port=config.get('options', 'db_port', fallback='5432'),
    user=config.get('options', 'db_user', fallback='odoo'),
    password=config.get('options', 'db_password', fallback='odoo'),
    dbname='postgres'
)
cursor = conn.cursor()

# Get all databases
cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;")
databases = [db[0] for db in cursor.fetchall()]
cursor.close()
conn.close()

print("Searching for MO WH/MO/00012 across databases...")
print("="*80)

# Try all databases
for db_name in databases:
    if db_name in ['postgres', 'template0', 'template1']:
        continue
    
    print(f"Checking database: {db_name}...", end=' ')
        
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=config.get('options', 'db_host', fallback='localhost'),
            port=config.get('options', 'db_port', fallback='5432'),
            user=config.get('options', 'db_user', fallback='odoo'),
            password=config.get('options', 'db_password', fallback='odoo'),
            dbname=db_name
        )
        cursor = conn.cursor()
        
        # Check if mrp_production table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'mrp_production'
            );
        """)
        
        
        if cursor.fetchone()[0]:
            print("has mrp_production")
            # Check for WH/MO/00012
            cursor.execute("""
                SELECT id, name, product_id, state
                FROM mrp_production 
                WHERE name = 'WH/MO/00012'
            """)
            
            result = cursor.fetchone()
            if not result:
                # List recent MOs
                cursor.execute("""
                    SELECT id, name, state, create_date
                    FROM mrp_production 
                    WHERE name LIKE 'WH/MO/%'
                    ORDER BY create_date DESC
                    LIMIT 5
                """)
                recent_mos = cursor.fetchall()
                if recent_mos:
                    print(f"     (not found, but has {len(recent_mos)} recent WH/MO/* orders)")
                    for mo in recent_mos:
                        print(f"       - {mo[1]} (state: {mo[2]})")
                else:
                    print("     (no WH/MO/* orders found)")
                cursor.close()
                conn.close()
                continue
                
            if result:
                print(f"\n✅ FOUND in database: {db_name}")
                print(f"   MO ID: {result[0]}")
                print(f"   MO Name: {result[1]}")
                print(f"   Product ID: {result[2]}")
                print(f"   State: {result[3]}")
                
                mo_id = result[0]
                
                # Get product name
                cursor.execute("""
                    SELECT pt.name->>'en_US' as name
                    FROM product_product pp
                    JOIN product_template pt ON pp.product_tmpl_id = pt.id
                    WHERE pp.id = %s
                """, (result[2],))
                product_name = cursor.fetchone()
                if product_name:
                    print(f"   Product: {product_name[0]}")
                
                # Get stock moves for raw materials
                cursor.execute("""
                    SELECT 
                        sm.id,
                        pp.id as product_id,
                        pt.name->>'en_US' as product_name,
                        sm.product_uom_qty,
                        sm.reserved_availability,
                        sm.quantity_done,
                        sm.state,
                        sm.scada_equipment_id,
                        me.name as equipment_name,
                        me.equipment_code
                    FROM stock_move sm
                    JOIN product_product pp ON sm.product_id = pp.id
                    JOIN product_template pt ON pp.product_tmpl_id = pt.id
                    LEFT JOIN maintenance_equipment me ON sm.scada_equipment_id = me.id
                    WHERE sm.raw_material_production_id = %s
                    ORDER BY pt.name, sm.id
                """, (mo_id,))
                
                moves = cursor.fetchall()
                
                print(f"\n   Raw Material Moves: {len(moves)}")
                print("   " + "="*76)
                
                from collections import defaultdict
                product_summary = defaultdict(lambda: {'qty': 0, 'reserved': 0, 'consumed': 0, 'moves': []})
                
                for move in moves:
                    move_id, prod_id, prod_name, qty, reserved, consumed, state, equip_id, equip_name, equip_code = move
                    
                    print(f"\n   Move ID: {move_id}")
                    print(f"     Product: [{prod_id}] {prod_name}")
                    print(f"     To Consume: {qty}")
                    print(f"     Reserved: {reserved}")
                    print(f"     Consumed: {consumed}")
                    print(f"     State: {state}")
                    print(f"     Equipment: {equip_name} ({equip_code})" if equip_name else "     Equipment: None")
                    
                    # Group by product ID (as API does)
                    product_summary[prod_id]['name'] = prod_name
                    product_summary[prod_id]['qty'] += qty
                    product_summary[prod_id]['reserved'] += reserved
                    product_summary[prod_id]['consumed'] += consumed
                    product_summary[prod_id]['moves'].append({
                        'id': move_id,
                        'qty': qty,
                        'equipment': f"{equip_name} ({equip_code})" if equip_name else "None"
                    })
                
                print("\n   " + "="*76)
                print("   API Response Summary (grouped by product):")
                print("   " + "="*76)
                
                for prod_id, data in product_summary.items():
                    if len(data['moves']) > 1:
                        print(f"\n   ⚠️  {data['name']}")
                        print(f"       API will return: {data['qty']} kg (SUM of {len(data['moves'])} moves)")
                        for m in data['moves']:
                            print(f"         - Move {m['id']}: {m['qty']} kg from {m['equipment']}")
                    else:
                        m = data['moves'][0]
                        print(f"\n   ✓ {data['name']}")
                        print(f"     API returns: {data['qty']} kg from {m['equipment']}")
                
                break
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error checking {db_name}: {e}")
        continue

print("\n" + "="*80)
