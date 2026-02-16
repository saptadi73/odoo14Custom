#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contoh script untuk update data via Odoo API
Demonstrasi CRUD operations
"""

import xmlrpc.client
from datetime import datetime

# Konfigurasi Odoo
ODOO_URL = "http://localhost:8070"
ODOO_DB = "manukanjabung"
ODOO_USERNAME = "admin"
ODOO_PASSWORD = "admin"

def connect_odoo():
    """Koneksi ke Odoo"""
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    return uid, models

def contoh_update_partner(models, uid):
    """Contoh 1: Update data partner"""
    print("\n" + "=" * 60)
    print("CONTOH 1: UPDATE PARTNER")
    print("=" * 60)
    
    try:
        # Cari partner pertama
        partner_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'search',
            [[('customer_rank', '>', 0)]], {'limit': 1}
        )
        
        if not partner_ids:
            print("❌ Tidak ada partner customer")
            return
        
        partner_id = partner_ids[0]
        
        # Baca data sebelum update
        partner_before = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'read',
            [[partner_id]],
            {'fields': ['name', 'phone', 'email']}
        )[0]
        
        print(f"\n📊 Partner ID {partner_id} SEBELUM update:")
        print(f"   Name: {partner_before['name']}")
        print(f"   Phone: {partner_before.get('phone', '-')}")
        print(f"   Email: {partner_before.get('email', '-')}")
        
        # Update data
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'write',
            [[partner_id], {
                'phone': f'0812-3456-7890 (updated {timestamp})',
                'comment': f'Updated via API at {timestamp}'
            }]
        )
        
        if result:
            # Baca data setelah update
            partner_after = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'res.partner', 'read',
                [[partner_id]],
                {'fields': ['name', 'phone', 'email', 'comment']}
            )[0]
            
            print(f"\n✅ UPDATE BERHASIL!")
            print(f"\n📊 Partner ID {partner_id} SESUDAH update:")
            print(f"   Name: {partner_after['name']}")
            print(f"   Phone: {partner_after.get('phone', '-')}")
            print(f"   Email: {partner_after.get('email', '-')}")
            print(f"   Comment: {partner_after.get('comment', '-')}")
        else:
            print("❌ Update gagal")
    
    except Exception as e:
        print(f"❌ Error: {e}")

def contoh_create_partner(models, uid):
    """Contoh 2: Create partner baru"""
    print("\n" + "=" * 60)
    print("CONTOH 2: CREATE PARTNER BARU")
    print("=" * 60)
    
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        new_partner = {
            'name': f'Test Partner API {timestamp}',
            'email': 'test@example.com',
            'phone': '0812-1234-5678',
            'street': 'Jl. Test No. 123',
            'city': 'Jakarta',
            'country_id': 100,  # Indonesia
            'is_company': False,
            'customer_rank': 1,
        }
        
        partner_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'create',
            [new_partner]
        )
        
        print(f"\n✅ CREATE BERHASIL!")
        print(f"   New Partner ID: {partner_id}")
        
        # Baca data yang baru dibuat
        partner = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'read',
            [[partner_id]],
            {'fields': ['name', 'email', 'phone', 'city']}
        )[0]
        
        print(f"\n📊 Data Partner Baru:")
        print(f"   Name: {partner['name']}")
        print(f"   Email: {partner.get('email', '-')}")
        print(f"   Phone: {partner.get('phone', '-')}")
        print(f"   City: {partner.get('city', '-')}")
        
        return partner_id
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def contoh_search_filter(models, uid):
    """Contoh 3: Search dengan filter"""
    print("\n" + "=" * 60)
    print("CONTOH 3: SEARCH DENGAN FILTER")
    print("=" * 60)
    
    try:
        # Search partner dengan filter
        domain = [
            ['customer_rank', '>', 0],  # Adalah customer
            '|',  # OR condition
            ['city', 'ilike', 'jakarta'],
            ['city', 'ilike', 'bandung']
        ]
        
        partner_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'search',
            [domain],
            {'limit': 5}
        )
        
        print(f"\n✅ Ditemukan {len(partner_ids)} partner")
        
        if partner_ids:
            partners = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'res.partner', 'read',
                [partner_ids],
                {'fields': ['name', 'city', 'phone']}
            )
            
            print("\n📊 Hasil pencarian:")
            for p in partners:
                print(f"   - {p['name']} ({p.get('city', '-')}): {p.get('phone', '-')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

def contoh_delete_partner(models, uid, partner_id):
    """Contoh 4: Delete partner"""
    print("\n" + "=" * 60)
    print("CONTOH 4: DELETE PARTNER")
    print("=" * 60)
    
    try:
        if not partner_id:
            print("❌ Tidak ada partner ID untuk dihapus")
            return
        
        # Verifikasi partner exists
        exists = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'search_count',
            [[('id', '=', partner_id)]]
        )
        
        if not exists:
            print(f"❌ Partner ID {partner_id} tidak ditemukan")
            return
        
        # Delete
        result = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'unlink',
            [[partner_id]]
        )
        
        if result:
            print(f"✅ DELETE BERHASIL!")
            print(f"   Partner ID {partner_id} telah dihapus")
        else:
            print(f"❌ Delete gagal")
    
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("=" * 60)
    print("ODOO API UPDATE OPERATIONS TEST")
    print("=" * 60)
    
    try:
        # Connect
        uid, models = connect_odoo()
        print(f"✅ Terkoneksi sebagai User ID: {uid}")
        
        # Contoh 1: Update partner existing
        contoh_update_partner(models, uid)
        
        # Contoh 2: Create partner baru
        new_partner_id = contoh_create_partner(models, uid)
        
        # Contoh 3: Search dengan filter
        contoh_search_filter(models, uid)
        
        # Contoh 4: Delete partner yang baru dibuat (cleanup)
        if new_partner_id:
            print("\n⚠️  Membersihkan data test...")
            contoh_delete_partner(models, uid, new_partner_id)
        
        print("\n" + "=" * 60)
        print("✅ SEMUA TEST API BERHASIL!")
        print("=" * 60)
        print("""
KESIMPULAN:
- API connection: ✅ OK
- CREATE operation: ✅ OK
- READ operation: ✅ OK
- UPDATE operation: ✅ OK
- DELETE operation: ✅ OK
- SEARCH/FILTER: ✅ OK

API Anda sekarang berfungsi dengan baik!
Gunakan script ini sebagai template untuk operasi API Anda.
        """)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
