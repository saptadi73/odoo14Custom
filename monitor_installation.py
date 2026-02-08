# -*- coding: utf-8 -*-
"""Monitor installation status"""
import psycopg2
import time
import sys

DB_CONFIG = {
    'dbname': 'manu14',
    'user': 'openpg',
    'password': 'openpgpwd',
    'host': 'localhost',
    'port': '5432'
}

modules_to_check = [
    'accounting_pdf_reports',
    'om_account_asset',
    'om_account_budget',
    'om_account_bank_statement_import',
    'om_account_accountant'
]

def check_installation_status():
    """Check current installation status"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("\n" + "="*70)
        print("INSTALLATION STATUS MONITOR")
        print("="*70 + "\n")
        
        for module in modules_to_check:
            cur.execute("""
                SELECT state FROM ir_module_module WHERE name = %s
            """, (module,))
            
            result = cur.fetchone()
            if result:
                state = result[0]
                if state == 'installed':
                    icon = "✅"
                    color = "INSTALLED"
                elif state == 'to install':
                    icon = "⏳"
                    color = "INSTALLING..."
                elif state == 'to upgrade':
                    icon = "🔄"
                    color = "UPGRADING..."
                elif state == 'uninstalled':
                    icon = "⬜"
                    color = "NOT INSTALLED"
                else:
                    icon = "❓"
                    color = state.upper()
                
                print(f"  {icon} {module:35} [{color}]")
        
        # Count installed
        cur.execute("""
            SELECT COUNT(*) FROM ir_module_module 
            WHERE name IN %s AND state = 'installed'
        """, (tuple(modules_to_check),))
        
        installed_count = cur.fetchone()[0]
        
        print("\n" + "="*70)
        print(f"Progress: {installed_count}/{len(modules_to_check)} modules installed")
        print("="*70 + "\n")
        
        if installed_count == len(modules_to_check):
            print("🎉 ALL MODULES SUCCESSFULLY INSTALLED!")
            print("\nNext steps:")
            print("1. Refresh your browser")
            print("2. Check the 'Accounting' menu")
            print("3. Go to Accounting → Reporting\n")
            return True
        else:
            print("ℹ️  Some modules are not yet installed.")
            print("\nIf you're installing now, please wait...")
            print("If installation is stuck, check the browser for any popup.\n")
            return False
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        return False

if __name__ == '__main__':
    check_installation_status()
