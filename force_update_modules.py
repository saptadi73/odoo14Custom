#!/usr/bin/env python3
# Force restart database dengan update semua modul terkait

import subprocess
import sys
import os

print("="*70)
print("FORCE DATABASE UPDATE - FIX REGISTRY")
print("="*70)

modules_to_update = [
    'accounting_pdf_reports',
    'account_dynamic_reports',
    'om_account_asset'
]

print(f"\nModul yang akan di-update: {', '.join(modules_to_update)}")
print("\nIni akan:")
print("1. Force reload semua model dari modul-modul ini")
print("2. Update registry database")
print("3. Memperbaiki semua KeyError yang berkaitan")

response = input("\nLanjutkan? (y/n): ")

if response.lower() != 'y':
    print("Dibatalkan.")
    sys.exit(0)

print("\n" + "="*70)
print("MENJALANKAN UPDATE...")
print("="*70)

cmd = [
    r'c:\odoo14c\python\python.exe',
    'odoo-bin',
    '-c', r'C:\addon14\odoo.conf',
    '-d', 'manu14',
    '-u', ','.join(modules_to_update),
    '--stop-after-init'
]

print(f"\nCommand: {' '.join(cmd)}")
print("\nMemulai update...\n")

try:
    os.chdir(r'C:\odoo14c\server')
    result = subprocess.run(cmd, capture_output=False, text=True)
    
    if result.returncode == 0:
        print("\n" + "="*70)
        print("✓ UPDATE BERHASIL!")
        print("="*70)
        print("\nLangkah selanjutnya:")
        print("1. Restart Odoo (tekan F5 di VS Code)")
        print("2. Clear browser cache")
        print("3. Login kembali")
        print("\nSemua KeyError harus sudah teratasi.")
    else:
        print("\n" + "="*70)
        print("⚠ UPDATE SELESAI DENGAN WARNING")
        print("="*70)
        print("Cek log di: c:\\addon14\\log\\odoo.log")
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    sys.exit(1)
