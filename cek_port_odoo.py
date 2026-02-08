#!/usr/bin/env python3
# Script untuk cek port Odoo yang sedang digunakan

import subprocess
import re

print("="*70)
print("CEK PORT ODOO YANG SEDANG DIGUNAKAN")
print("="*70)

# Port-port umum untuk Odoo
ports_to_check = [8069, 8070, 8071, 8072]

print("\nMemeriksa port Odoo...\n")

try:
    # Jalankan netstat untuk cek port yang listening
    result = subprocess.run(
        ['netstat', '-ano'],
        capture_output=True,
        text=True
    )
    
    output = result.stdout
    
    found_any = False
    
    for port in ports_to_check:
        # Cari baris yang mengandung port dan LISTENING
        pattern = f'TCP.*:({port}).*LISTENING\\s+(\\d+)'
        matches = re.findall(pattern, output)
        
        if matches:
            found_any = True
            for match in matches:
                port_num = match[0]
                pid = match[1]
                
                # Cari nama proses dari PID
                tasklist_result = subprocess.run(
                    ['tasklist', '/FI', f'PID eq {pid}', '/FO', 'CSV', '/NH'],
                    capture_output=True,
                    text=True
                )
                
                process_name = "Unknown"
                if tasklist_result.stdout:
                    # Parse CSV output
                    parts = tasklist_result.stdout.split(',')
                    if len(parts) > 0:
                        process_name = parts[0].strip('"')
                
                print(f"✓ Port {port_num} - DIGUNAKAN")
                print(f"  Process: {process_name}")
                print(f"  PID: {pid}")
                
                # Cek apakah ini Odoo
                if 'python' in process_name.lower():
                    print(f"  ⚠ Kemungkinan ini adalah Odoo instance!")
                    print(f"  Untuk stop: taskkill /F /PID {pid}")
                
                print()
    
    # Cek port yang tidak digunakan
    for port in ports_to_check:
        pattern = f'TCP.*:{port}.*LISTENING'
        if not re.search(pattern, output):
            print(f"✗ Port {port} - BEBAS (tidak digunakan)")
    
    if not found_any:
        print("Tidak ada Odoo instance yang sedang berjalan pada port umum.")
    
    print("\n" + "="*70)
    print("INFORMASI INSTANCE INI:")
    print("="*70)
    print("Port: 8070")
    print("Config: c:\\addon14\\odoo.conf")
    print("Database: manu14")
    print("URL: http://localhost:8070")
    
    print("\n" + "="*70)
    print("COMMAND BERGUNA:")
    print("="*70)
    print("\nUntuk start Odoo di port 8070:")
    print("  python c:\\addon14\\restart_odoo.py")
    print("  Kemudian tekan F5 di VS Code")
    print("\nUntuk stop proses tertentu:")
    print("  taskkill /F /PID <nomor_PID>")
    print("\nUntuk stop semua Python (hati-hati!):")
    print("  taskkill /F /IM python.exe")
    
except Exception as e:
    print(f"Error: {e}")
    print("\nJika error, coba jalankan sebagai Administrator")
