#!/usr/bin/env python3
# Quick fix for accounting.report KeyError

import subprocess
import sys
import os

print("="*60)
print("FIXING accounting.report KeyError")
print("="*60)

# Solution 1: Upgrade the module
print("\nSOLUTION 1: Upgrade accounting_pdf_reports module")
print("-" * 60)
print("Run this command:\n")
print('cd C:\\odoo14c\\server')
print('python odoo-bin -c C:\\addon14\\odoo.conf -d manu14 -u accounting_pdf_reports --stop-after-init')
print()

# Solution 2: Direct SQL fix
print("\nSOLUTION 2: Remove orphaned actions (if upgrade doesn't work)")
print("-" * 60)
print("If the module is not properly installed, run SQL commands:")
print()
print("psql -U odoo -d manu14")
print()
print("-- Check actions:")
print("SELECT id, name, res_model FROM ir_act_window WHERE res_model = 'accounting.report';")
print()
print("-- If you want to remove them (BACKUP FIRST):")
print("-- DELETE FROM ir_act_window WHERE res_model = 'accounting.report';")
print()

# Solution 3: Install/Reinstall
print("\nSOLUTION 3: Reinstall the module")
print("-" * 60)
print("1. Go to Odoo > Apps")
print("2. Remove 'Apps' filter")  
print("3. Search for 'accounting_pdf_reports'")
print("4. If installed: Upgrade or Uninstall then Reinstall")
print("5. If not installed: Install it")
print()

print("\nRECOMMENDED: Try Solution 1 first (module upgrade)")
print("="*60)
