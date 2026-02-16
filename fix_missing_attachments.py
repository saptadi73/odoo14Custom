#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to fix missing attachment files in Odoo filestore
Handles FileNotFoundError for ir.attachment records
"""

import xmlrpc.client
import os
import sys

# Konfigurasi Odoo
ODOO_URL = "http://localhost:8070"
ODOO_DB = "manukanjabung"
ODOO_USERNAME = "admin"
ODOO_PASSWORD = "admin"

# Lokasi filestore
FILESTORE_PATH = r"C:\Users\sapta\AppData\Local\OpenERP S.A\Odoo\filestore\manukanjabung"

def connect_odoo():
    """Koneksi ke Odoo via XML-RPC"""
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        
        if not uid:
            print("❌ Gagal autentikasi. Periksa username/password")
            return None, None, None
        
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        print(f"✅ Terkoneksi sebagai user ID: {uid}")
        return common, uid, models
    
    except Exception as e:
        print(f"❌ Error koneksi: {e}")
        return None, None, None

def check_attachment_file_exists(store_fname):
    """Check if physical file exists in filestore"""
    if not store_fname:
        return True  # File disimpan di database, bukan filestore
    
    # Replace forward slash with backslash for Windows
    file_path = os.path.join(FILESTORE_PATH, store_fname.replace('/', '\\'))
    return os.path.exists(file_path)

def find_broken_attachments(models, uid):
    """Find all attachments with missing physical files"""
    print("\n🔍 Mencari attachment dengan file yang hilang...")
    
    try:
        # Get all attachments that should have files in filestore
        attachment_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.attachment', 'search',
            [[('store_fname', '!=', False)]]
        )
        
        print(f"📊 Total attachment di filestore: {len(attachment_ids)}")
        
        if not attachment_ids:
            print("✅ Tidak ada attachment di filestore")
            return []
        
        # Read attachment data
        attachments = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.attachment', 'read',
            [attachment_ids],
            {'fields': ['id', 'name', 'store_fname', 'res_model', 'res_id', 'type']}
        )
        
        broken_attachments = []
        
        for att in attachments:
            if not check_attachment_file_exists(att.get('store_fname')):
                broken_attachments.append(att)
                print(f"   ❌ ID {att['id']}: {att['name']} - File hilang: {att.get('store_fname')}")
        
        print(f"\n📊 Total attachment rusak: {len(broken_attachments)}")
        return broken_attachments
    
    except Exception as e:
        print(f"❌ Error saat mencari attachment: {e}")
        return []

def fix_broken_attachments(models, uid, broken_attachments, method='delete'):
    """
    Fix broken attachments
    method: 'delete' or 'reset'
    - delete: Hapus record attachment yang rusak
    - reset: Reset ke database storage (datas menjadi False)
    """
    
    if not broken_attachments:
        print("✅ Tidak ada attachment yang perlu diperbaiki")
        return
    
    print(f"\n🔧 Memperbaiki {len(broken_attachments)} attachment dengan metode: {method}")
    
    fixed_count = 0
    failed_count = 0
    
    for att in broken_attachments:
        try:
            if method == 'delete':
                # Delete the broken attachment record
                result = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'ir.attachment', 'unlink',
                    [[att['id']]]
                )
                
                if result:
                    print(f"   ✅ Deleted ID {att['id']}: {att['name']}")
                    fixed_count += 1
                else:
                    print(f"   ❌ Failed to delete ID {att['id']}")
                    failed_count += 1
            
            elif method == 'reset':
                # Reset to database storage (clear store_fname and datas)
                result = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'ir.attachment', 'write',
                    [[att['id']], {
                        'store_fname': False,
                        'datas': False,
                        'db_datas': False
                    }]
                )
                
                if result:
                    print(f"   ✅ Reset ID {att['id']}: {att['name']}")
                    fixed_count += 1
                else:
                    print(f"   ❌ Failed to reset ID {att['id']}")
                    failed_count += 1
        
        except Exception as e:
            print(f"   ❌ Error fixing ID {att['id']}: {e}")
            failed_count += 1
    
    print(f"\n📊 Hasil perbaikan:")
    print(f"   ✅ Berhasil: {fixed_count}")
    print(f"   ❌ Gagal: {failed_count}")

def main():
    print("=" * 60)
    print("ODOO ATTACHMENT FILESTORE REPAIR TOOL")
    print("=" * 60)
    
    # Connect to Odoo
    common, uid, models = connect_odoo()
    
    if not uid:
        return
    
    # Find broken attachments
    broken_attachments = find_broken_attachments(models, uid)
    
    if not broken_attachments:
        print("\n✅ Semua attachment dalam kondisi baik!")
        return
    
    # Show summary
    print("\n" + "=" * 60)
    print("RINGKASAN ATTACHMENT RUSAK")
    print("=" * 60)
    
    model_count = {}
    for att in broken_attachments:
        model = att.get('res_model', 'unknown')
        model_count[model] = model_count.get(model, 0) + 1
    
    for model, count in sorted(model_count.items(), key=lambda x: -x[1]):
        print(f"   {model}: {count} attachment")
    
    # Ask for action
    print("\n" + "=" * 60)
    print("PILIHAN PERBAIKAN:")
    print("=" * 60)
    print("1. DELETE - Hapus record attachment yang rusak (RECOMMENDED)")
    print("2. RESET - Reset ke database storage (data akan hilang)")
    print("3. CANCEL - Batal, tidak melakukan perubahan")
    print()
    
    choice = input("Pilih metode perbaikan (1/2/3): ").strip()
    
    if choice == '1':
        confirm = input(f"\n⚠️  Yakin hapus {len(broken_attachments)} attachment? (yes/no): ").strip().lower()
        if confirm == 'yes':
            fix_broken_attachments(models, uid, broken_attachments, method='delete')
        else:
            print("❌ Dibatalkan")
    
    elif choice == '2':
        confirm = input(f"\n⚠️  Yakin reset {len(broken_attachments)} attachment? (yes/no): ").strip().lower()
        if confirm == 'yes':
            fix_broken_attachments(models, uid, broken_attachments, method='reset')
        else:
            print("❌ Dibatalkan")
    
    else:
        print("❌ Dibatalkan")
    
    print("\n" + "=" * 60)
    print("SELESAI")
    print("=" * 60)

if __name__ == "__main__":
    main()
