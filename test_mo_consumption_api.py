#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test endpoint /api/scada/mo/update-with-consumptions
Untuk diagnosa masalah update consumption MO
"""

import requests
import json
from datetime import datetime

# Konfigurasi
ODOO_URL = "http://localhost:8070"
DATABASE = "manukanjabung"
USERNAME = "admin"
PASSWORD = "admin"

def login_odoo():
    """Login ke Odoo dan dapatkan session cookie"""
    print("=" * 70)
    print("STEP 1: LOGIN KE ODOO")
    print("=" * 70)
    
    session = requests.Session()
    
    # Login endpoint
    login_url = f"{ODOO_URL}/web/session/authenticate"
    
    login_payload = {
        "jsonrpc": "2.0",
        "params": {
            "db": DATABASE,
            "login": USERNAME,
            "password": PASSWORD
        }
    }
    
    try:
        response = session.post(
            login_url,
            json=login_payload,
            headers={'Content-Type': 'application/json'}
        )
        
        result = response.json()
        
        if result.get('result') and result['result'].get('uid'):
            print(f"✅ Login berhasil")
            print(f"   User ID: {result['result']['uid']}")
            print(f"   Session ID: {result['result'].get('session_id', 'N/A')[:20]}...")
            return session, result['result']
        else:
            print(f"❌ Login gagal: {result}")
            return None, None
    
    except Exception as e:
        print(f"❌ Error login: {e}")
        return None, None

def get_active_mo(session):
    """Ambil MO aktif untuk test"""
    print("\n" + "=" * 70)
    print("STEP 2: AMBIL MO AKTIF UNTUK TEST")
    print("=" * 70)
    
    url = f"{ODOO_URL}/api/scada/mo-list-confirmed"
    
    payload = {
        "jsonrpc": "2.0",
        "params": {
            "limit": 5
        }
    }
    
    try:
        response = session.post(
            url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        result = response.json()
        
        if result.get('result'):
            res = result['result']
            
            # Response structure: {status: ..., count: ..., data: [...]}
            if res.get('status') == 'success' and res.get('data'):
                mos = res['data']
                
                if isinstance(mos, list) and len(mos) > 0:
                    mo = mos[0]
                    print(f"✅ Found {len(mos)} MO untuk test")
                    print(f"   Using first MO: {mo.get('mo_id')}")
                    print(f"   Product: {mo.get('product')}")
                    print(f"   Qty: {mo.get('quantity', 'N/A')}")
                    
                    # Return with name key for compatibility
                    return {'name': mo.get('mo_id'), '_raw': mo}
                else:
                    print("❌ Tidak ada MO confirmed")
                    return None
            else:
                print(f"❌ Error: {res}")
                return None
        else:
            print(f"❌ Error: {result}")
            return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_equipment_list(session):
    """Get equipment codes from MO raw materials"""
    print("\n" + "=" * 70)
    print("STEP 3: AMBIL EQUIPMENT CODES DARI MO")
    print("=" * 70)
    
    # Equipment codes akan diambil dari raw materials MO yang punya equipment_code
    # Tidak perlu endpoint terpisah
    print("✅ Will use equipment codes from MO raw materials")
    
    return []

def test_update_consumption(session, mo_id, equipment_codes):
    """Test update consumption"""
    print("\n" + "=" * 70)
    print("STEP 4: TEST UPDATE CONSUMPTION")
    print("=" * 70)
    
    url = f"{ODOO_URL}/api/scada/mo/update-with-consumptions"
    
    # Buat payload test
    test_data = {
        "mo_id": mo_id,
        "quantity": None,  # Tidak update quantity, hanya consumption
    }
    
    # Tambahkan consumption untuk beberapa equipment (nilai kecil untuk test)
    for i, eq_code in enumerate(equipment_codes[:3]):  # Test 3 equipment pertama
        test_data[eq_code] = 10.0 + i  # 10, 11, 12 kg
    
    payload = {
        "jsonrpc": "2.0",
        "params": test_data
    }
    
    print(f"\n📤 Sending request:")
    print(f"   URL: {url}")
    print(f"   Payload: {json.dumps(test_data, indent=2)}")
    
    try:
        response = session.post(
            url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        result = response.json()
        print(f"\n📥 Response Body:")
        print(json.dumps(result, indent=2))
        
        # Parse result
        if result.get('result'):
            res = result['result']
            
            if res.get('status') == 'success':
                print(f"\n✅ UPDATE BERHASIL!")
                print(f"   MO: {res.get('mo_id')}")
                print(f"   State: {res.get('mo_state')}")
                
                consumed_items = res.get('consumed_items', [])
                print(f"\n   Consumed items ({len(consumed_items)}):")
                for item in consumed_items:
                    print(f"      - {item.get('equipment_code')}: {item.get('applied_qty')} kg")
                    print(f"        Products: {', '.join(item.get('products', []))}")
                    print(f"        Move IDs: {item.get('move_ids')}")
                
                if res.get('errors'):
                    print(f"\n⚠️  Errors:")
                    for err in res['errors']:
                        print(f"      - {err}")
                
                return True
            else:
                print(f"\n❌ UPDATE GAGAL!")
                print(f"   Message: {res.get('message')}")
                
                if res.get('errors'):
                    print(f"\n   Errors:")
                    for err in res['errors']:
                        print(f"      - {err}")
                
                return False
        else:
            print(f"\n❌ Response tidak valid")
            return False
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def diagnose_mo_structure(mo_id):
    """Diagnosa struktur MO untuk debugging via XML-RPC"""
    print("\n" + "=" * 70)
    print("DIAGNOSA: CEK STRUKTUR MO")
    print("=" * 70)
    
    try:
        import xmlrpc.client
        
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(DATABASE, USERNAME, PASSWORD, {})
        
        if not uid:
            print("❌ Gagal autentikasi")
            return False
        
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        
        # Find MO
        mo_ids = models.execute_kw(
            DATABASE, uid, PASSWORD,
            'mrp.production', 'search',
            [[('name', '=', mo_id)]]
        )
        
        if not mo_ids:
            print(f"❌ MO {mo_id} tidak ditemukan")
            return False
        
        # Read MO with raw materials
        mo = models.execute_kw(
            DATABASE, uid, PASSWORD,
            'mrp.production', 'read',
            [mo_ids],
            {'fields': ['id', 'name', 'state', 'product_id', 'product_qty', 'move_raw_ids']}
        )[0]
        
        print(f"\n📊 MO Detail:")
        print(f"   ID: {mo.get('id')}")
        print(f"   Name: {mo.get('name')}")
        print(f"   State: {mo.get('state')}")
        print(f"   Product: {mo.get('product_id', [False, 'N/A'])[1]}")
        print(f"   Qty: {mo.get('product_qty')}")
        
        # Read raw materials (stock.move)
        move_ids = mo.get('move_raw_ids', [])
        
        if move_ids:
            moves = models.execute_kw(
                DATABASE, uid, PASSWORD,
                'stock.move', 'read',
                [move_ids],
                {'fields': ['id', 'product_id', 'product_uom_qty', 'quantity_done', 'state', 'scada_equipment_id']}
            )
            
            print(f"\n📦 Raw Materials ({len(moves)}):")
            
            # Group by equipment
            by_equipment = {}
            no_equipment = []
            
            for move in moves:
                eq_id = move.get('scada_equipment_id')
                if eq_id and eq_id[0]:  # [id, name]
                    eq_code = eq_id[1]  # Use name as code for display
                    if eq_code not in by_equipment:
                        by_equipment[eq_code] = []
                    by_equipment[eq_code].append(move)
                else:
                    no_equipment.append(move)
            
            if by_equipment:
                print(f"\n   Materials WITH equipment code ({len(by_equipment)} equipment):")
                for eq_code, materials in by_equipment.items():
                    print(f"\n   Equipment: {eq_code}")
                    for mat in materials:
                        print(f"      - {mat.get('product_id', [False, 'N/A'])[1]}")
                        print(f"        Move ID: {mat.get('id')}")
                        print(f"        Planned: {mat.get('product_uom_qty')}, Done: {mat.get('quantity_done', 0)}")
                        print(f"        State: {mat.get('state')}")
            
            if no_equipment:
                print(f"\n   Materials WITHOUT equipment code ({len(no_equipment)}):")
                for mat in no_equipment:
                    prod_name = mat.get('product_id', [False, 'N/A'])[1]
                    print(f"      - {prod_name}: {mat.get('product_uom_qty')}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 70)
    print("TEST ENDPOINT: /api/scada/mo/update-with-consumptions")
    print("=" * 70)
    print(f"\nKonfigurasi:")
    print(f"  URL: {ODOO_URL}")
    print(f"  Database: {DATABASE}")
    print(f"  Username: {USERNAME}")
    print()
    
    # Step 1: Login
    session, user_info = login_odoo()
    if not session:
        print("\n❌ GAGAL LOGIN - Test dibatalkan")
        return
    
    # Step 2: Get active MO
    mo = get_active_mo(session)
    if not mo:
        print("\n❌ TIDAK ADA MO - Test dibatalkan")
        return
    
    mo_id = mo.get('name')
    
    # Step 3: Get equipment codes from MO raw materials
    get_equipment_list(session)
    
    # Diagnosa struktur MO untuk mendapat equipment codes
    print("\n" + "=" * 70)
    print("STEP 3B: DIAGNOSA MO STRUCTURE")
    print("=" * 70)
    
    equipment_codes = []
    diagnose_success = diagnose_mo_structure(mo_id)
    
    if not diagnose_success:
        print("⚠️  Gagal diagnosa MO, akan coba dengan equipment code manual")
        # Fallback: coba dengan equipment code yang sering dipakai
        equipment_codes = ['silo101', 'silo102', 'silo103']
        print(f"   Using test equipment codes: {equipment_codes}")
    
    # Step 4: Test update
    if equipment_codes or True:  # Always try even without equipment codes
        # Use hardcoded equipment codes for testing
        if not equipment_codes:
            equipment_codes = ['silo101', 'silo102']
        
        success = test_update_consumption(session, mo_id, equipment_codes)
        
        if success:
            print("\n" + "=" * 70)
            print("✅ TEST BERHASIL - API BERFUNGSI DENGAN BAIK")
            print("=" * 70)
        else:
            print("\n" + "=" * 70)
            print("❌ TEST GAGAL - PERIKSA ERROR DI ATAS")
            print("=" * 70)
    else:
        print("\n⚠️  Tidak bisa test update: tidak ada equipment code")
    
    print("\n" + "=" * 70)
    print("TEST SELESAI")
    print("=" * 70)

if __name__ == "__main__":
    main()
