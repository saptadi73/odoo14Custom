# -*- coding: utf-8 -*-
"""Quick check for stuck modules"""
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
    
    # Check stuck modules
    cur.execute("""
        SELECT name, state 
        FROM ir_module_module 
        WHERE state IN ('to install', 'to upgrade', 'to remove')
        ORDER BY name
    """)
    
    stuck_modules = cur.fetchall()
    
    if stuck_modules:
        print(f"\n⚠️  FOUND {len(stuck_modules)} STUCK MODULE(S):\n")
        for name, state in stuck_modules:
            print(f"   - {name}: {state}")
        
        print("\n" + "="*70)
        print("TO FIX THIS, RUN: python fix_stuck_modules.py")
        print("="*70 + "\n")
    else:
        print("\n✅ No stuck modules. Database is clean!\n")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ ERROR: {e}\n")
