#!/usr/bin/env python3
"""
Grant Accounting Access to Users
This script grants accounting/billing permissions to specified users
"""

import psycopg2
import sys

# Database configuration
DB_CONFIG = {
    'dbname': 'manu14',
    'user': 'openpg',
    'password': 'openpgpwd',
    'host': 'localhost',
    'port': 5432
}

def grant_accounting_access():
    """Grant accounting access to all active users or specific user"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("\n" + "="*80)
        print("📋 CURRENT ACTIVE USERS:")
        print("="*80)
        
        # Get all active users
        cur.execute("""
            SELECT id, login
            FROM res_users 
            WHERE active = true 
            ORDER BY id
        """)
        users = cur.fetchall()
        
        for user in users:
            print(f"ID: {user[0]}, Login: {user[1]}")
        
        print("\n" + "="*80)
        print("🔍 ACCOUNTING GROUPS:")
        print("="*80)
        
        # Get accounting groups
        cur.execute("""
            SELECT id, name, category_id
            FROM res_groups 
            WHERE name LIKE '%Account%' 
               OR name LIKE '%Billing%'
               OR name LIKE '%Invoic%'
            ORDER BY id
        """)
        groups = cur.fetchall()
        
        accounting_groups = []
        for group in groups:
            print(f"Group ID: {group[0]}, Name: {group[1]}")
            if 'Accountant' in group[1] or 'Billing' in group[1]:
                accounting_groups.append(group[0])
        
        if not accounting_groups:
            print("\n⚠️ No accounting groups found! Finding by module...")
            # Try to find by module
            cur.execute("""
                SELECT g.id, g.name 
                FROM res_groups g
                JOIN ir_module_category c ON g.category_id = c.id
                WHERE c.name = 'Accounting'
                   OR g.name IN ('Accountant', 'Billing', 'Billing Administrator')
            """)
            groups = cur.fetchall()
            for group in groups:
                print(f"Found: Group ID: {group[0]}, Name: {group[1]}")
                accounting_groups.append(group[0])
        
        if not accounting_groups:
            print("\n❌ ERROR: No accounting groups found in database!")
            print("This might mean the accounting module didn't install properly.")
            return
        
        print(f"\n✅ Found {len(accounting_groups)} accounting group(s)")
        print("\n" + "="*80)
        print("🔧 GRANTING ACCOUNTING ACCESS TO ALL USERS:")
        print("="*80)
        
        # Grant access to all users
        for user in users:
            user_id = user[0]
            user_login = user[1]
            
            print(f"\n👤 Processing user: {user_login} (ID: {user_id})")
            
            for group_id in accounting_groups:
                # Check if already has access
                cur.execute("""
                    SELECT 1 FROM res_groups_users_rel 
                    WHERE uid = %s AND gid = %s
                """, (user_id, group_id))
                
                if cur.fetchone():
                    print(f"   ✓ Already has access to group {group_id}")
                else:
                    # Grant access
                    cur.execute("""
                        INSERT INTO res_groups_users_rel (uid, gid)
                        VALUES (%s, %s)
                    """, (user_id, group_id))
                    print(f"   ✅ Granted access to group {group_id}")
        
        # Commit changes
        conn.commit()
        
        print("\n" + "="*80)
        print("✅ SUCCESS! Accounting access granted to all users!")
        print("="*80)
        print("\n🔄 Now do this:")
        print("1. LOGOUT from Odoo (if logged in)")
        print("2. Clear browser cache or open in Incognito/Private mode")
        print("3. LOGIN again")
        print("4. Menu 'Accounting' should now appear!\n")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    grant_accounting_access()
