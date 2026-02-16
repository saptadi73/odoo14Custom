#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test update consumption untuk MO dengan state 'progress'
"""

import requests
import json

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

def test_update_progress_mo(session):
    """Test update MO dengan state 'progress'"""
    print("\n" + "=" * 70)
    print("TEST: UPDATE MO DENGAN STATE 'PROGRESS'")
    print("=" * 70)
    
    # MO WH/MO/00001 sudah dalam state 'progress'
    mo_id = "WH/MO/00001"
    
    url = f"{ODOO_URL}/api/scada/mo/update-with-consumptions"
    
    test_data = {
        "mo_id": mo_id,
        "silo101": 15.0,  # Test update 15 kg
        "silo102": 20.0,  # Test update 20 kg
    }
    
    payload = {
        "jsonrpc": "2.0",
        "params": test_data
    }
    
    print(f"\n📤 Updating MO: {mo_id} (state: progress)")
    print(f"   Payload: {json.dumps(test_data, indent=2)}")
    
    response = session.post(
        url,
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    result = response.json()
    
    if result.get('result'):
        res = result['result']
        
        if res.get('status') == 'success':
            print(f"\n✅ UPDATE BERHASIL untuk MO state 'progress'!")
            print(f"   MO: {res.get('mo_id')}")
            print(f"   State: {res.get('mo_state')}")
            
            consumed_items = res.get('consumed_items', [])
            print(f"\n   Consumed items ({len(consumed_items)}):")
            for item in consumed_items:
                print(f"      - {item.get('equipment_code')}: {item.get('applied_qty')} kg")
                print(f"        Products: {', '.join(item.get('products', []))}")
            
            if res.get('errors'):
                print(f"\n⚠️  Errors:")
                for err in res['errors']:
                    print(f"      - {err}")
            
            return True
        else:
            print(f"\n❌ UPDATE GAGAL!")
            print(f"   Message: {res.get('message')}")
            return False
    else:
        print(f"\n❌ Response error: {result}")
        return False

def test_update_confirmed_again(session):
    """Test update MO confirmed lagi (untuk perbandingan)"""
    print("\n" + "=" * 70)
    print("TEST: UPDATE MO DENGAN STATE 'CONFIRMED'")
    print("=" * 70)
    
    # MO WH/MO/00004 masih confirmed
    mo_id = "WH/MO/00004"
    
    url = f"{ODOO_URL}/api/scada/mo/update-with-consumptions"
    
    test_data = {
        "mo_id": mo_id,
        "silo101": 25.0,
        "silo103": 30.0,
    }
    
    payload = {
        "jsonrpc": "2.0",
        "params": test_data
    }
    
    print(f"\n📤 Updating MO: {mo_id} (state: confirmed)")
    print(f"   Payload: {json.dumps(test_data, indent=2)}")
    
    response = session.post(
        url,
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    result = response.json()
    
    if result.get('result'):
        res = result['result']
        
        if res.get('status') == 'success':
            print(f"\n✅ UPDATE BERHASIL untuk MO state 'confirmed'!")
            print(f"   MO: {res.get('mo_id')}")
            print(f"   State: {res.get('mo_state')}")
            
            consumed_items = res.get('consumed_items', [])
            print(f"\n   Consumed items ({len(consumed_items)}):")
            for item in consumed_items:
                print(f"      - {item.get('equipment_code')}: {item.get('applied_qty')} kg")
            
            return True
        else:
            print(f"\n❌ UPDATE GAGAL!")
            print(f"   Message: {res.get('message')}")
            return False

def main():
    print("=" * 70)
    print("TEST: UPDATE CONSUMPTION - CONFIRMED vs PROGRESS")
    print("=" * 70)
    
    session = login_odoo()
    if not session:
        return
    
    # Test 1: Update MO yang sudah 'progress'
    success1 = test_update_progress_mo(session)
    
    # Test 2: Update MO yang masih 'confirmed'
    success2 = test_update_confirmed_again(session)
    
    print("\n" + "=" * 70)
    print("KESIMPULAN")
    print("=" * 70)
    
    if success1 and success2:
        print("\n✅ Endpoint bisa update MO dengan state:")
        print("   - 'confirmed' ✅")
        print("   - 'progress' ✅")
        print("\n📝 Catatan:")
        print("   - Ketika MO 'confirmed' di-update, state otomatis menjadi 'progress'")
        print("   - MO 'progress' bisa terus di-update berkali-kali")
        print("   - Tidak ada pembatasan state di endpoint ini")
    elif success1:
        print("\n✅ MO 'progress' bisa di-update")
        print("❌ MO 'confirmed' gagal di-update")
    elif success2:
        print("\n❌ MO 'progress' gagal di-update")
        print("✅ MO 'confirmed' bisa di-update")
    else:
        print("\n❌ Kedua test gagal")

if __name__ == "__main__":
    main()
