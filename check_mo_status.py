#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check MO status dan buat MO test jika perlu
"""

import xmlrpc.client

ODOO_URL = "http://localhost:8070"
ODOO_DB = "manukanjabung"
ODOO_USERNAME = "admin"
ODOO_PASSWORD = "admin"

def main():
    print("=" * 70)
    print("CHECK MO STATUS")
    print("=" * 70)
    
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        
        if not uid:
            print("❌ Gagal autentikasi")
            return
        
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        print(f"✅ Terkoneksi sebagai User ID: {uid}\n")
        
        # Check all MO states
        print("📊 MO by State:")
        print("-" * 70)
        
        states = ['draft', 'confirmed', 'progress', 'done', 'cancel']
        
        for state in states:
            count = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'mrp.production', 'search_count',
                [[('state', '=', state)]]
            )
            
            icon = "✅" if count > 0 else "  "
            print(f"   {icon} {state.upper()}: {count} MO")
            
            if count > 0 and count <= 5:
                # Show some examples
                mo_ids = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'mrp.production', 'search',
                    [[('state', '=', state)]],
                    {'limit': 5}
                )
                
                mos = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'mrp.production', 'read',
                    [mo_ids],
                    {'fields': ['name', 'product_id', 'product_qty', 'state']}
                )
                
                for mo in mos:
                    prod_name = mo.get('product_id', [False, 'N/A'])[1]
                    print(f"        - {mo['name']}: {prod_name} ({mo['product_qty']})")
        
        print()
        
        # Check total MO
        total_count = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mrp.production', 'search_count',
            [[]]
        )
        
        print(f"   TOTAL: {total_count} MO")
        
        # Suggest action
        print("\n" + "=" * 70)
        print("REKOMENDASI:")
        print("=" * 70)
        
        confirmed_count = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mrp.production', 'search_count',
            [[('state', '=', 'confirmed')]]
        )
        
        if confirmed_count == 0:
            print("\n⚠️  Tidak ada MO dengan state 'confirmed'")
            print("\nUntuk test API update-with-consumptions, Anda perlu:")
            print("1. Buat MO baru di Odoo")
            print("2. Confirm MO tersebut (button 'Confirm')")
            print("3. Pastikan MO punya raw materials dengan equipment code")
            print("\nATAU")
            print("\nUpdate MO yang sudah ada ke state 'confirmed'")
            
            # Check if there are draft MOs
            draft_count = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'mrp.production', 'search_count',
                [[('state', '=', 'draft')]]
            )
            
            if draft_count > 0:
                print(f"\n💡 Ada {draft_count} MO dalam state 'draft'")
                print("   Anda bisa confirm salah satunya untuk test")
                
                confirm = input("\nConfirm MO pertama? (y/n): ").strip().lower()
                
                if confirm == 'y':
                    mo_ids = models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'mrp.production', 'search',
                        [[('state', '=', 'draft')]],
                        {'limit': 1}
                    )
                    
                    if mo_ids:
                        mo_id = mo_ids[0]
                        
                        # Confirm MO
                        result = models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'mrp.production', 'action_confirm',
                            [[mo_id]]
                        )
                        
                        mo = models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'mrp.production', 'read',
                            [[mo_id]],
                            {'fields': ['name', 'state']}
                        )[0]
                        
                        print(f"\n✅ MO {mo['name']} berhasil di-confirm!")
                        print(f"   State: {mo['state']}")
                        print("\nSekarang bisa test API dengan:")
                        print("    python test_mo_consumption_api.py")
        else:
            print(f"\n✅ Ada {confirmed_count} MO dalam state 'confirmed'")
            print("\nAnda bisa langsung test API dengan:")
            print("    python test_mo_consumption_api.py")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
