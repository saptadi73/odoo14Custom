#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Odoo API connection and diagnose issues
"""

import xmlrpc.client
import sys

# Konfigurasi Odoo
ODOO_URL = "http://localhost:8070"
ODOO_DB = "manukanjabung"
ODOO_USERNAME = "admin"
ODOO_PASSWORD = "admin"

def test_connection():
    """Test basic connection"""
    print("=" * 60)
    print("TEST 1: Koneksi Dasar")
    print("=" * 60)
    
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        version = common.version()
        print(f"✅ Server terhubung")
        print(f"   Version: {version.get('server_version')}")
        print(f"   Series: {version.get('server_serie')}")
        return common
    except Exception as e:
        print(f"❌ Gagal koneksi: {e}")
        return None

def test_authentication(common):
    """Test authentication"""
    print("\n" + "=" * 60)
    print("TEST 2: Autentikasi")
    print("=" * 60)
    
    try:
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        
        if uid:
            print(f"✅ Autentikasi berhasil")
            print(f"   User ID: {uid}")
            print(f"   Database: {ODOO_DB}")
            return uid
        else:
            print(f"❌ Autentikasi gagal")
            print(f"   Periksa username/password")
            return None
    except Exception as e:
        print(f"❌ Error autentikasi: {e}")
        return None

def test_model_access(uid):
    """Test model access"""
    print("\n" + "=" * 60)
    print("TEST 3: Akses Model")
    print("=" * 60)
    
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    
    test_models = [
        'res.partner',
        'res.users',
        'ir.attachment',
        'account.move',
        'account.account'
    ]
    
    for model in test_models:
        try:
            # Test search access
            result = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                model, 'search',
                [[]], {'limit': 1}
            )
            print(f"   ✅ {model}: Access OK")
        except Exception as e:
            print(f"   ❌ {model}: {str(e)[:50]}")
    
    return models

def test_attachment_operations(models, uid):
    """Test attachment operations specifically"""
    print("\n" + "=" * 60)
    print("TEST 4: Operasi Attachment")
    print("=" * 60)
    
    try:
        # Count attachments
        count = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.attachment', 'search_count',
            [[]]
        )
        print(f"   ✅ Total attachment: {count}")
        
        # Get sample attachments
        att_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.attachment', 'search',
            [[]], {'limit': 5}
        )
        
        if att_ids:
            attachments = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'ir.attachment', 'read',
                [att_ids],
                {'fields': ['id', 'name', 'type', 'store_fname']}
            )
            
            print(f"\n   Sample 5 attachment:")
            for att in attachments:
                storage = "filestore" if att.get('store_fname') else "database"
                print(f"   - ID {att['id']}: {att['name']} [{storage}]")
        
        return True
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_read_operations(models, uid):
    """Test reading user data (common failing operation)"""
    print("\n" + "=" * 60)
    print("TEST 5: Operasi Read User/Partner")
    print("=" * 60)
    
    try:
        # Read current user
        user = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.users', 'read',
            [[uid]],
            {'fields': ['id', 'name', 'login', 'partner_id']}
        )[0]
        
        print(f"   ✅ User read OK: {user['name']}")
        
        # Try to read user image (often fails with missing files)
        try:
            user_with_image = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'res.users', 'read',
                [[uid]],
                {'fields': ['id', 'name', 'image_128']}
            )[0]
            
            if user_with_image.get('image_128'):
                print(f"   ✅ User image read OK")
            else:
                print(f"   ⚠️  User tidak punya image")
        
        except Exception as e:
            print(f"   ❌ User image read gagal: {str(e)[:100]}")
        
        return True
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_write_operations(models, uid):
    """Test write operations"""
    print("\n" + "=" * 60)
    print("TEST 6: Operasi Write (Update)")
    print("=" * 60)
    
    try:
        # Try to update user's own data (safe test)
        # Just update something harmless like notification_type
        result = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.users', 'write',
            [[uid], {'notification_type': 'inbox'}]  # Just set to inbox
        )
        
        if result:
            print(f"   ✅ Write operation berhasil")
        else:
            print(f"   ❌ Write operation gagal")
        
        return result
    
    except Exception as e:
        print(f"   ❌ Error write: {e}")
        return False

def main():
    print("=" * 60)
    print("ODOO API CONNECTION TEST & DIAGNOSTIC")
    print("=" * 60)
    print(f"\nKonfigurasi:")
    print(f"  URL: {ODOO_URL}")
    print(f"  Database: {ODOO_DB}")
    print(f"  Username: {ODOO_USERNAME}")
    print()
    
    # Test 1: Connection
    common = test_connection()
    if not common:
        return
    
    # Test 2: Authentication
    uid = test_authentication(common)
    if not uid:
        return
    
    # Test 3: Model Access
    models = test_model_access(uid)
    
    # Test 4: Attachment Operations
    test_attachment_operations(models, uid)
    
    # Test 5: Read Operations
    test_read_operations(models, uid)
    
    # Test 6: Write Operations
    test_write_operations(models, uid)
    
    print("\n" + "=" * 60)
    print("KESIMPULAN")
    print("=" * 60)
    print("""
Jika ada error pada TEST 4 atau TEST 5 terkait attachment/image,
jalankan script: python fix_missing_attachments.py

Jika ada error pada TEST 6 (write operations),
periksa permission dan access rights untuk user.
    """)

if __name__ == "__main__":
    main()
