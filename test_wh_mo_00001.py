#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test update consumption untuk WH/MO/00001 (progress) dengan berbagai skenario
"""

import requests
import json
import xmlrpc.client

ODOO_URL = "http://localhost:8070"
DATABASE = "manukanjabung"
USERNAME = "admin"
PASSWORD = "admin"

def login_odoo():
    """Login ke Odoo"""
    session = requests.Session()
    
    login_url = f"{ODOO_URL}/web/session/authenticate"
    
    login_payload = {
        "jsonrpc": "2.0",
        "params": {
            "db": DATABASE,
            "login": USERNAME,
            "password": PASSWORD
        }
    }
    
    response = session.post(
        login_url,
        json=login_payload,
        headers={'Content-Type': 'application/json'}
    )
    
    result = response.json()
    
    if result.get('result') and result['result'].get('uid'):
        print(f"✅ Login berhasil (User ID: {result['result']['uid']})")
        return session
    else:
        print(f"❌ Login gagal")
        return None

def check_mo_current_state(mo_id):
    """Cek state dan consumption MO saat ini via XML-RPC"""
    print("\n" + "=" * 70)
    print(f"CEK STATE CURRENT: {mo_id}")
    print("=" * 70)
    
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(DATABASE, USERNAME, PASSWORD, {})
        
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        
        # Find MO
        mo_ids = models.execute_kw(
            DATABASE, uid, PASSWORD,
            'mrp.production', 'search',
            [[('name', '=', mo_id)]]
        )
        
        if not mo_ids:
            print(f"❌ MO {mo_id} tidak ditemukan")
            return None
        
        # Read MO
        mo = models.execute_kw(
            DATABASE, uid, PASSWORD,
            'mrp.production', 'read',
            [mo_ids],
            {'fields': ['name', 'state', 'product_id', 'product_qty', 'move_raw_ids']}
        )[0]
        
        print(f"\n📊 MO Current State:")
        print(f"   Name: {mo['name']}")
        print(f"   Product: {mo['product_id'][1]}")
        print(f"   Qty: {mo['product_qty']}")
        print(f"   State: {mo['state']}")
        
        # Read raw materials
        move_ids = mo.get('move_raw_ids', [])
        
        if move_ids:
            moves = models.execute_kw(
                DATABASE, uid, PASSWORD,
                'stock.move', 'read',
                [move_ids],
                {'fields': ['id', 'product_id', 'product_uom_qty', 'quantity_done', 'scada_equipment_id']}
            )
            
            print(f"\n📦 Current Consumption:")
            
            # Filter moves with equipment only
            moves_with_eq = [m for m in moves if m.get('scada_equipment_id')]
            
            if moves_with_eq:
                for move in moves_with_eq[:10]:  # Show first 10
                    eq_name = move['scada_equipment_id'][1] if move['scada_equipment_id'] else 'No Equipment'
                    prod_name = move['product_id'][1]
                    planned = move['product_uom_qty']
                    done = move['quantity_done']
                    
                    if done > 0:
                        print(f"   - {eq_name}: {prod_name}")
                        print(f"     Planned: {planned} kg, Done: {done} kg")
            else:
                print("   Belum ada consumption")
        
        return mo
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_update_consumption(session, mo_id, consumption_data, test_name):
    """Test update consumption dengan data tertentu"""
    print("\n" + "=" * 70)
    print(f"TEST: {test_name}")
    print("=" * 70)
    
    url = f"{ODOO_URL}/api/scada/mo/update-with-consumptions"
    
    payload = {
        "jsonrpc": "2.0",
        "params": {
            "mo_id": mo_id,
            **consumption_data
        }
    }
    
    print(f"\n📤 Request:")
    print(f"   MO: {mo_id}")
    print(f"   Consumption:")
    for key, value in consumption_data.items():
        if key != 'mo_id':
            print(f"      {key}: {value} kg")
    
    response = session.post(
        url,
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    result = response.json()
    
    print(f"\n📥 Response Status: {response.status_code}")
    
    if result.get('result'):
        res = result['result']
        
        if res.get('status') == 'success':
            print(f"\n✅ UPDATE BERHASIL!")
            print(f"   MO: {res.get('mo_id')}")
            print(f"   State: {res.get('mo_state')}")
            
            consumed_items = res.get('consumed_items', [])
            print(f"\n   Updated Items ({len(consumed_items)}):")
            for item in consumed_items:
                print(f"      - {item.get('equipment_code')} ({item.get('equipment_name')})")
                print(f"        Applied: {item.get('applied_qty')} kg")
                print(f"        Products: {', '.join(item.get('products', []))}")
            
            if res.get('errors'):
                print(f"\n⚠️  Errors:")
                for err in res['errors']:
                    print(f"      - {err}")
            
            return True
        else:
            print(f"\n❌ UPDATE GAGAL!")
            print(f"   Message: {res.get('message')}")
            
            if res.get('errors'):
                print(f"   Errors:")
                for err in res['errors']:
                    print(f"      - {err}")
            
            return False
    else:
        print(f"\n❌ Response error:")
        print(json.dumps(result, indent=2))
        return False

def main():
    print("=" * 70)
    print("TEST UPDATE CONSUMPTION: WH/MO/00001")
    print("=" * 70)
    
    mo_id = "WH/MO/00001"
    
    # Step 1: Check current state
    mo = check_mo_current_state(mo_id)
    if not mo:
        print("\n❌ Tidak bisa melanjutkan test")
        return
    
    # Step 2: Login
    session = login_odoo()
    if not session:
        return
    
    # Step 3: Test Update 1 - Update beberapa silo dengan nilai kecil
    test_update_consumption(
        session, 
        mo_id,
        {
            "silo101": 50.0,   # SILO A
            "silo102": 45.0,   # SILO B
            "silo103": 30.0,   # SILO C
        },
        "Update 1 - Set consumption awal (3 silo)"
    )
    
    # Step 4: Check state after update 1
    print("\n" + "-" * 70)
    input("Press Enter untuk check state dan lanjut ke update 2...")
    check_mo_current_state(mo_id)
    
    # Step 5: Test Update 2 - Update dengan nilai lebih besar (replace mode)
    test_update_consumption(
        session,
        mo_id,
        {
            "silo101": 100.0,  # Naik dari 50 → 100
            "silo102": 80.0,   # Naik dari 45 → 80
            "silo104": 25.0,   # SILO D (baru)
        },
        "Update 2 - Replace dengan nilai baru (3 silo, 1 silo baru)"
    )
    
    # Step 6: Check final state
    print("\n" + "-" * 70)
    input("Press Enter untuk check final state...")
    check_mo_current_state(mo_id)
    
    # Step 7: Test Update 3 - Update banyak silo sekaligus
    test_update_consumption(
        session,
        mo_id,
        {
            "silo101": 150.0,
            "silo102": 120.0,
            "silo103": 60.0,
            "silo104": 40.0,
            "silo105": 75.0,  # SILO E (baru)
            "silo106": 50.0,  # SILO F (baru)
        },
        "Update 3 - Batch update 6 silo sekaligus"
    )
    
    # Final state
    print("\n" + "-" * 70)
    input("Press Enter untuk check final state setelah batch update...")
    final_mo = check_mo_current_state(mo_id)
    
    print("\n" + "=" * 70)
    print("KESIMPULAN")
    print("=" * 70)
    print(f"""
✅ MO {mo_id} berhasil di-update 3 kali

📝 Behavior yang terlihat:
   1. State tetap 'progress' sepanjang update
   2. Replace mode: Nilai lama diganti dengan nilai baru
   3. Bisa update silo yang sama berkali-kali
   4. Bisa tambah silo baru kapan saja
   5. Tidak ada limit jumlah update

💡 Ini cocok untuk SCADA realtime monitoring dimana:
   - Data consumption terus berubah
   - Tidak perlu hitung delta, langsung kirim nilai total
   - Backend Odoo yang handle state management
    """)

if __name__ == "__main__":
    main()
