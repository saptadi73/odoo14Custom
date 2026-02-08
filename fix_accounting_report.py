#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix accounting.report KeyError
This script will:
1. Check if accounting_pdf_reports module is installed
2. Remove orphaned action records referencing accounting.report
3. Update the module if needed
"""

import xmlrpc.client
import getpass

# Configuration
url = 'http://localhost:8069'
db = 'manu14'
username = 'admin'

# Get password
password = getpass.getpass('Enter admin password: ')

# Connect
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})

if not uid:
    print("Authentication failed!")
    exit(1)

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

print(f"Connected as uid: {uid}")

# Check if accounting_pdf_reports is installed
print("\n1. Checking accounting_pdf_reports module status...")
module = models.execute_kw(db, uid, password, 'ir.module.module', 'search_read', 
    [[['name', '=', 'accounting_pdf_reports']]], 
    {'fields': ['name', 'state']})

if module:
    print(f"   Module state: {module[0]['state']}")
    if module[0]['state'] != 'installed':
        print("   ⚠ Module is not installed!")
        response = input("   Do you want to install it? (y/n): ")
        if response.lower() == 'y':
            models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_install', [[module[0]['id']]])
            print("   ✓ Module installation initiated")
    else:
        print("   ✓ Module is installed")
        # Try upgrading the module
        response = input("   Do you want to upgrade the module? (y/n): ")
        if response.lower() == 'y':
            models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_upgrade', [[module[0]['id']]])
            print("   ✓ Module upgrade initiated")
else:
    print("   ⚠ Module not found in database!")

# Find actions referencing accounting.report
print("\n2. Searching for actions with res_model='accounting.report'...")
actions = models.execute_kw(db, uid, password, 'ir.actions.act_window', 'search_read',
    [[['res_model', '=', 'accounting.report']]],
    {'fields': ['name', 'res_model', 'view_mode']})

if actions:
    print(f"   Found {len(actions)} action(s):")
    for action in actions:
        print(f"   - ID: {action['id']}, Name: {action['name']}")
else:
    print("   No actions found")

# Check if the model exists in ir.model
print("\n3. Checking if accounting.report model exists in ir.model...")
model_record = models.execute_kw(db, uid, password, 'ir.model', 'search_read',
    [[['model', '=', 'accounting.report']]],
    {'fields': ['model', 'name']})

if model_record:
    print(f"   ✓ Model found: {model_record[0]['name']}")
else:
    print("   ⚠ Model not found in ir.model table")
    print("   This might indicate the module didn't load properly")

# Check for menu items referencing the actions
if actions:
    print("\n4. Checking for menu items referencing these actions...")
    action_ids = [a['id'] for a in actions]
    for action_id in action_ids:
        menus = models.execute_kw(db, uid, password, 'ir.ui.menu', 'search_read',
            [[['action', '=', f'ir.actions.act_window,{action_id}']]],
            {'fields': ['name', 'action']})
        if menus:
            for menu in menus:
                print(f"   - Menu: {menu['name']} (ID: {menu['id']}) -> Action: {action_id}")

print("\n" + "="*60)
print("Diagnosis complete!")
print("\nRecommended actions:")
print("1. Restart Odoo server with -u accounting_pdf_reports")
print("2. Or upgrade the module from Odoo UI")
print("3. If issue persists, the module may have loading errors")
