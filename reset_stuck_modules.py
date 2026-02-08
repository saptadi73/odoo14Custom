# -*- coding: utf-8 -*-
"""
Script untuk reset stuck module installation di Odoo
Run this with: python reset_stuck_modules.py
"""
import psycopg2
import sys

# Database configuration
DB_CONFIG = {
    'dbname': 'manu14',
    'user': 'openpg',
    'password': 'openpgpwd',
    'host': 'localhost',
    'port': '5432'
}

def reset_module_states():
    """Reset module states that are stuck in 'to install', 'to upgrade', or 'to remove'"""
    
    try:
        print("=" * 70)
        print("RESET STUCK MODULE INSTALLATION")
        print("=" * 70)
        
        # Connect to database
        print(f"\n1. Connecting to database '{DB_CONFIG['dbname']}'...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Check stuck modules
        print("\n2. Checking for stuck modules...")
        cur.execute("""
            SELECT name, state 
            FROM ir_module_module 
            WHERE state IN ('to install', 'to upgrade', 'to remove')
            ORDER BY name
        """)
        
        stuck_modules = cur.fetchall()
        
        if not stuck_modules:
            print("   ✅ No stuck modules found. Database is clean!")
            cur.close()
            conn.close()
            return
        
        print(f"\n   ⚠️  Found {len(stuck_modules)} stuck module(s):")
        for name, state in stuck_modules:
            print(f"      - {name}: {state}")
        
        # Ask for confirmation
        print("\n3. Do you want to reset these modules to 'uninstalled' state?")
        print("   This will cancel any pending installation/upgrade/removal.")
        response = input("   Type 'yes' to continue or 'no' to cancel: ").strip().lower()
        
        if response != 'yes':
            print("\n   ❌ Operation cancelled by user.")
            cur.close()
            conn.close()
            return
        
        # Reset module states
        print("\n4. Resetting module states...")
        cur.execute("""
            UPDATE ir_module_module 
            SET state = 'uninstalled' 
            WHERE state IN ('to install', 'to upgrade', 'to remove')
        """)
        
        affected_rows = cur.rowcount
        
        # Commit changes
        conn.commit()
        print(f"   ✅ Successfully reset {affected_rows} module(s)")
        
        # Close connection
        cur.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("SUCCESS!")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Refresh your browser (F5)")
        print("2. Go to Apps and try to install the module again")
        print("3. If the issue persists, check the error message\n")
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ ERROR: Could not connect to database")
        print(f"   Details: {e}")
        print("\n   Please check:")
        print("   - PostgreSQL is running")
        print("   - Database credentials are correct")
        print("   - Database 'manu14' exists")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)

if __name__ == '__main__':
    reset_module_states()
