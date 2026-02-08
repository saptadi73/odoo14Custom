#!/usr/bin/env python3
# Fix accounting.report model loading issue

import sys
import psycopg2

# Database connection settings
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'manu14'
DB_USER = 'odoo'
DB_PASSWORD = 'odoo'

print("="*70)
print("FIX ACCOUNTING.REPORT MODEL ISSUE")
print("="*70)

try:
    # Connect to database
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    
    print("\n1. Checking ir.model for accounting.report...")
    cur.execute("""
        SELECT id, model, name FROM ir_model 
        WHERE model = 'accounting.report'
    """)
    model = cur.fetchone()
    
    if model:
        print(f"   ✓ Model found: ID={model[0]}, Name={model[2]}")
    else:
        print("   ⚠ Model NOT found in ir_model")
    
    print("\n2. Checking ir.actions.act_window referencing accounting.report...")
    cur.execute("""
        SELECT id, name, res_model FROM ir_act_window 
        WHERE res_model = 'accounting.report'
    """)
    actions = cur.fetchall()
    
    if actions:
        print(f"   Found {len(actions)} action(s):")
        for action in actions:
            print(f"   - ID: {action[0]}, Name: {action[1]}")
    else:
        print("   No actions found")
    
    print("\n3. Checking module installation status...")
    cur.execute("""
        SELECT name, state FROM ir_module_module 
        WHERE name = 'accounting_pdf_reports'
    """)
    module = cur.fetchone()
    
    if module:
        print(f"   Module: {module[0]}")
        print(f"   State: {module[1]}")
        
        if module[1] != 'installed':
            print(f"\n   ⚠ Module is '{module[1]}', not 'installed'!")
            print("   Installing module...")
            cur.execute("""
                UPDATE ir_module_module 
                SET state = 'to install'
                WHERE name = 'accounting_pdf_reports'
            """)
            conn.commit()
            print("   ✓ Module marked for installation")
            print("\n   Run: odoo-bin -d manu14 --stop-after-init")
    else:
        print("   ✗ Module not found in database!")
    
    print("\n4. Checking for orphaned menu items...")
    cur.execute("""
        SELECT m.id, m.name, m.action 
        FROM ir_ui_menu m 
        WHERE m.action LIKE 'ir.actions.act_window,%'
        AND CAST(SUBSTRING(m.action FROM 23) AS INTEGER) IN (
            SELECT id FROM ir_act_window WHERE res_model = 'accounting.report'
        )
    """)
    menus = cur.fetchall()
    
    if menus:
        print(f"   Found {len(menus)} menu(s) referencing accounting.report actions:")
        for menu in menus:
            print(f"   - ID: {menu[0]}, Name: {menu[1]}, Action: {menu[2]}")
    
    # Close connection
    cur.close()
    conn.close()
    
    print("\n" + "="*70)
    print("DIAGNOSIS COMPLETE")
    print("="*70)
    print("\nRECOMMENDED ACTIONS:")
    print("1. Restart Odoo with: -u accounting_pdf_reports --stop-after-init")
    print("2. Clear browser cache")
    print("3. If issue persists, reinstall the module")
    
except psycopg2.OperationalError as e:
    print(f"\n✗ Database connection failed: {e}")
    print("\nTrying alternative fix method...")
    print("\nRun this command:")
    print("cd C:\\odoo14c\\server")
    print("python odoo-bin -c C:\\addon14\\odoo.conf -d manu14 -u accounting_pdf_reports --stop-after-init")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    sys.exit(1)
