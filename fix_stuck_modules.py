# -*- coding: utf-8 -*-
"""Fix stuck modules - Auto reset without confirmation"""
import psycopg2

DB_CONFIG = {
    'dbname': 'manu14',
    'user': 'openpg',
    'password': 'openpgpwd',
    'host': 'localhost',
    'port': '5432'
}

try:
    print("\n" + "="*70)
    print("FIXING STUCK MODULES")
    print("="*70)
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Check stuck modules first
    cur.execute("""
        SELECT name, state 
        FROM ir_module_module 
        WHERE state IN ('to install', 'to upgrade', 'to remove')
    """)
    
    stuck_modules = cur.fetchall()
    
    if not stuck_modules:
        print("\n✅ No stuck modules found.\n")
        cur.close()
        conn.close()
        exit(0)
    
    print(f"\nFound {len(stuck_modules)} stuck module(s):")
    for name, state in stuck_modules:
        print(f"  - {name}: {state}")
    
    # Reset them
    print("\nResetting to 'uninstalled' state...")
    cur.execute("""
        UPDATE ir_module_module 
        SET state = 'uninstalled' 
        WHERE state IN ('to install', 'to upgrade', 'to remove')
    """)
    
    conn.commit()
    print(f"✅ Reset {cur.rowcount} module(s)\n")
    
    print("="*70)
    print("DONE! Now refresh your browser and try installing again.")
    print("="*70 + "\n")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ ERROR: {e}\n")
