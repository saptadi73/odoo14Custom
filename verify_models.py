#!/usr/bin/env python3
# Verifikasi model-model sudah dimuat dengan benar

import subprocess
import sys

print("="*70)
print("VERIFIKASI MODEL REGISTRY")
print("="*70)

# Models yang harus ada
required_models = [
    'accounting.report',
    'ins.general.ledger',
    'ins.partner.ledger', 
    'ins.trial.balance',
    'ins.partner.ageing',
    'ins.financial.report'
]

print("\nMemeriksa model-model di log startup terakhir...\n")

try:
    # Baca log
    with open(r'c:\addon14\log\odoo.log', 'r', encoding='utf-8', errors='ignore') as f:
        log_content = f.read()
    
    # Cari di log
    found_models = []
    missing_models = []
    
    for model in required_models:
        # Cek apakah model disebutkan dalam log (sebagai tanda dimuat)
        if model in log_content:
            found_models.append(model)
        else:
            missing_models.append(model)
    
    # Cek warning "has no _description" yang menandakan model dimuat
    lines = log_content.split('\n')
    loaded_models = []
    for line in lines[-1000:]:  # Cek 1000 baris terakhir
        if 'has no _description' in line:
            for model in required_models:
                if model in line and model not in loaded_models:
                    loaded_models.append(model)
                    if model not in found_models:
                        found_models.append(model)
    
    print("Status Model:")
    print("-" * 70)
    
    all_ok = True
    for model in required_models:
        if model in found_models or model in loaded_models:
            print(f"  ✓ {model}")
        else:
            print(f"  ✗ {model} - NOT FOUND")
            all_ok = False
    
    print("\n" + "="*70)
    if all_ok:
        print("✓ SEMUA MODEL SUDAH DIMUAT")
        print("="*70)
        print("\nLangkah selanjutnya:")
        print("1. Restart Odoo (tekan F5 di VS Code atau gunakan restart_odoo.py)")
        print("2. Clear browser cache (Ctrl + Shift + Delete)")
        print("3. Reload halaman dan login")
        print("\nSemua error KeyError harus sudah hilang!")
    else:
        print("⚠ ADA MODEL YANG BELUM DIMUAT")
        print("="*70)
        print("\nCoba jalankan:")
        print("python force_update_modules.py")
        
except Exception as e:
    print(f"✗ Error membaca log: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("INFO TAMBAHAN")
print("="*70)
print("\nJika masih ada error setelah restart:")
print("1. Pastikan tidak ada proses Odoo lain yang berjalan")
print("2. Hapus folder __pycache__ di modul bermasalah:")
print("   - account_dynamic_reports")
print("   - accounting_pdf_reports")
print("   - om_account_asset")
print("3. Restart dengan update paksa semua modul")
