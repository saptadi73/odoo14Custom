# -*- coding: utf-8 -*-
"""Check installed accounting modules"""
import psycopg2

DB_CONFIG = {
    'dbname': 'manu14',
    'user': 'openpg',
    'password': 'openpgpwd',
    'host': 'localhost',
    'port': '5432'
}

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("\n" + "="*70)
    print("INSTALLED ACCOUNTING MODULES")
    print("="*70 + "\n")
    
    # Check for accounting modules
    cur.execute("""
        SELECT name, state, author
        FROM ir_module_module 
        WHERE (name LIKE '%account%' OR category_id IN (
            SELECT id FROM ir_module_category WHERE name LIKE '%Account%'
        ))
        AND state IN ('installed', 'to upgrade', 'to install')
        ORDER BY state DESC, name
    """)
    
    modules = cur.fetchall()
    
    if modules:
        print("Found modules:")
        for name, state, author in modules:
            icon = "✅" if state == "installed" else "⏳"
            print(f"  {icon} {name:40} [{state:12}] {author or ''}")
    else:
        print("  ⚠️  No accounting modules installed yet")
    
    print("\n" + "="*70)
    print("CUSTOM ACCOUNTING MODULES STATUS")
    print("="*70 + "\n")
    
    custom_modules = [
        'account_dynamic_reports',
        'accounting_pdf_reports',
        'om_account_accountant',
        'om_account_asset',
        'om_account_budget',
        'om_account_bank_statement_import',
        'account_reconciliation_widget'
    ]
    
    for mod_name in custom_modules:
        cur.execute("""
            SELECT state FROM ir_module_module WHERE name = %s
        """, (mod_name,))
        
        result = cur.fetchone()
        if result:
            state = result[0]
            if state == 'installed':
                icon = "✅"
            elif state == 'uninstalled':
                icon = "⬜"
            else:
                icon = "⏳"
            print(f"  {icon} {mod_name:40} [{state}]")
        else:
            print(f"  ❓ {mod_name:40} [NOT FOUND IN DB]")
    
    print("\n")
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ ERROR: {e}\n")
