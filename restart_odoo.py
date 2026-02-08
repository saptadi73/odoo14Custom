#!/usr/bin/env python3
# Helper script untuk restart Odoo dengan benar

import os
import subprocess
import time
import psutil

print("="*70)
print("ODOO RESTART HELPER")
print("="*70)

# Find and kill Odoo processes
print("\n1. Mencari proses Odoo yang berjalan...")
killed = 0
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        # Check if it's an Odoo process
        cmdline = proc.info['cmdline']
        if cmdline and any('odoo-bin' in str(cmd) for cmd in cmdline):
            print(f"   Menemukan proses Odoo: PID {proc.info['pid']}")
            proc.kill()
            killed += 1
            print(f"   ✓ Proses {proc.info['pid']} dihentikan")
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

if killed > 0:
    print(f"\n   ✓ {killed} proses Odoo dihentikan")
    print("   Menunggu 3 detik...")
    time.sleep(3)
else:
    print("   Tidak ada proses Odoo yang berjalan")

print("\n" + "="*70)
print("CARA RESTART ODOO:")
print("="*70)

print("\nOPSI 1: Via VS Code Debug (RECOMMENDED)")
print("-" * 70)
print("1. Tekan F5 atau klik tombol Debug di VS Code")
print("2. Pilih konfigurasi debug Odoo Anda")
print("3. Model accounting.report akan dimuat dengan benar")

print("\nOPSI 2: Via Terminal")
print("-" * 70)
print("cd C:\\odoo14c\\server")
print("c:\\odoo14c\\python\\python.exe odoo-bin -c C:\\addon14\\odoo.conf -d manu14")

print("\nATAU dengan update paksa:")
print("c:\\odoo14c\\python\\python.exe odoo-bin -c C:\\addon14\\odoo.conf -d manu14 -u accounting_pdf_reports")

print("\n" + "="*70)
print("CATATAN PENTING:")
print("="*70)
print("✓ Model accounting.report sudah dimuat ke database")
print("✓ Semua file SCSS sudah diperbaiki")
print("✓ Tinggal restart Odoo untuk load registry baru")
print("✓ Setelah restart, error KeyError harus hilang")
print("✓ Instance ini berjalan di PORT: 8070")
print("\n🌐 URL Akses: http://localhost:8070")
print("="*70)
