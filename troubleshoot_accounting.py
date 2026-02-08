# -*- coding: utf-8 -*-
"""
Script untuk troubleshoot instalasi modul Odoo Accounting
"""

print("="*70)
print("TROUBLESHOOTING GUIDE - INSTALASI MODUL ACCOUNTING")
print("="*70)

print("\n🔍 KEMUNGKINAN PENYEBAB GAGAL INSTALL:\n")

print("1. ❌ MODUL 'Invoicing' atau 'Accounting' BELUM TERINSTALL")
print("   Solusi:")
print("   - Buka Apps di Odoo")
print("   - Cari 'Invoicing' atau 'Accounting'")
print("   - Klik 'Install' pada salah satu modul tersebut")
print("   - Tunggu sampai selesai")
print("   - Baru install modul custom Accounting\n")

print("2. ❌ DEPENDENCY MODULE BELUM TERINSTALL")
print("   Untuk 'om_account_accountant', install ini dulu:")
print("   - accounting_pdf_reports")
print("   - om_account_asset")
print("   - om_account_budget")
print("   - om_account_bank_statement_import\n")

print("3. ❌ DATABASE DALAM MODE 'TO INSTALL/UPGRADE'")
print("   Solusi:")
print("   - Refresh halaman browser (F5)")
print("   - Atau restart Odoo server\n")

print("4. ❌ PERMISSION / ACCESS RIGHTS ERROR")
print("   Pastikan login sebagai Administrator\n")

print("5. ❌ DATA XML / VIEW ERROR")
print("   Cek log file untuk detail error\n")

print("="*70)
print("LANGKAH INSTALASI YANG BENAR:")
print("="*70)

print("\nUntuk 'account_dynamic_reports':")
print("  1. Install 'Invoicing' app dulu")
print("  2. Apps → Hapus filter 'Apps'")
print("  3. Cari: 'Dynamic Financial Reports'")
print("  4. Klik Install\n")

print("Untuk 'accounting_pdf_reports':")
print("  1. Install 'Invoicing' app dulu")
print("  2. Apps → Hapus filter 'Apps'")
print("  3. Cari: 'Odoo 14 Accounting Financial Reports'")
print("  4. Klik Install\n")

print("Untuk 'om_account_accountant' (FULL PACKAGE):")
print("  1. Install 'Invoicing' app dulu")
print("  2. Install dependencies secara berurutan:")
print("     a. accounting_pdf_reports")
print("     b. om_account_asset")
print("     c. om_account_budget")
print("     d. om_account_bank_statement_import")
print("  3. Baru install 'om_account_accountant'\n")

print("="*70)
print("CEK ERROR DI ODOO:")
print("="*70)
print("\n1. Aktifkan Developer Mode")
print("2. Klik install pada modul")
print("3. Jika error, akan muncul popup dengan detail error")
print("4. Copy paste error tersebut untuk troubleshooting\n")

print("="*70)
