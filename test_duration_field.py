#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Equipment Failure Duration Field
Contoh testing equipment failure API dengan field duration
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8069"
API_BASE = f"{BASE_URL}/api/scada"

# Credentials
DB = "your_database"
LOGIN = "admin"
PASSWORD = "admin"

# Session untuk menyimpan cookies
session = requests.Session()


def authenticate():
    """Login ke Odoo dan simpan session cookie"""
    print("=" * 60)
    print("Authenticating to Odoo...")
    print("=" * 60)
    
    url = f"{API_BASE}/authenticate"
    payload = {
        "db": DB,
        "login": LOGIN,
        "password": PASSWORD
    }
    
    response = session.post(url, json=payload)
    result = response.json()
    
    if result.get('status') == 'error':
        print(f"❌ Authentication failed: {result.get('message')}")
        exit(1)
    
    print(f"✓ Successfully authenticated")
    print(f"  UID: {result.get('uid')}")
    print(f"  Db: {result.get('db')}")
    print()


def create_equipment_failure_with_duration():
    """Create equipment failure dengan duration field"""
    print("=" * 60)
    print("Creating Equipment Failure with Duration Field...")
    print("=" * 60)
    
    url = f"{API_BASE}/equipment-failure"
    
    # Example 1: With duration
    payload = {
        "equipment_code": "PLC01",
        "description": "Motor overload saat proses mixing",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "duration": "02:30"  # 2 jam 30 menit
    }
    
    print("\nPayload:")
    print(json.dumps(payload, indent=2))
    
    response = session.post(url, json=payload)
    result = response.json()
    
    print("\nResponse:")
    print(json.dumps(result, indent=2))
    
    if result.get('status') == 'success':
        print(f"\n✓ Equipment failure created successfully")
        print(f"  ID: {result['data']['id']}")
        print(f"  Equipment: {result['data']['equipment_code']} ({result['data']['equipment_name']})")
        print(f"  Duration: {result['data']['duration']} ({result['data']['duration_minutes']} minutes)")
        return result['data']['id']
    else:
        print(f"\n❌ Failed to create equipment failure: {result.get('message')}")
        return None


def create_equipment_failure_without_duration():
    """Create equipment failure tanpa duration (optional field)"""
    print("\n" + "=" * 60)
    print("Creating Equipment Failure WITHOUT Duration Field...")
    print("=" * 60)
    
    url = f"{API_BASE}/equipment-failure"
    
    # Example 2: Without duration (optional field)
    payload = {
        "equipment_code": "PLC01",
        "description": "Electrical short circuit issue",
        "date": "2026-02-15 10:00:00"
        # No duration field
    }
    
    print("\nPayload:")
    print(json.dumps(payload, indent=2))
    
    response = session.post(url, json=payload)
    result = response.json()
    
    print("\nResponse:")
    print(json.dumps(result, indent=2))
    
    if result.get('status') == 'success':
        print(f"\n✓ Equipment failure created successfully (without duration)")
        print(f"  ID: {result['data']['id']}")
    else:
        print(f"\n❌ Failed: {result.get('message')}")


def get_equipment_failures():
    """Get list of equipment failures dengan duration field"""
    print("\n" + "=" * 60)
    print("Getting Equipment Failure List...")
    print("=" * 60)
    
    url = f"{API_BASE}/equipment-failure"
    params = {
        "equipment_code": "PLC01",
        "limit": 50
    }
    
    response = session.get(url, params=params)
    result = response.json()
    
    print("\nResponse:")
    print(json.dumps(result, indent=2))
    
    if result.get('status') == 'success':
        print(f"\n✓ Retrieved {result.get('count')} equipment failures")
        for failure in result.get('data', []):
            print(f"\n  - ID: {failure['id']}")
            print(f"    Equipment: {failure['equipment_code']}")
            print(f"    Description: {failure['description']}")
            print(f"    Date: {failure['date']}")
            print(f"    Duration: {failure.get('duration', 'N/A')}")
            print(f"    Duration (minutes): {failure.get('duration_minutes', 'N/A')}")
    else:
        print(f"\n❌ Failed to get failures: {result.get('message')}")


def get_equipment_failure_report():
    """Get equipment failure report dengan duration field"""
    print("\n" + "=" * 60)
    print("Getting Equipment Failure Report (Frontend)...")
    print("=" * 60)
    
    url = f"{API_BASE}/equipment-failure-report"
    
    payload = {
        "equipment_code": "PLC01",
        "period": "this_month",
        "limit": 100
    }
    
    print("\nPayload:")
    print(json.dumps(payload, indent=2))
    
    response = session.post(url, json=payload)
    result = response.json()
    
    print("\nResponse (partial):")
    data = result.copy()
    if 'data' in data and len(data['data']) > 0:
        data['data'] = data['data'][:2]  # Show only first 2 for brevity
    print(json.dumps(data, indent=2))
    
    if result.get('status') == 'success':
        print(f"\n✓ Retrieved equipment failure report")
        print(f"  Total failures: {result['summary']['total_failures']}")
        print(f"  Total equipment: {result['summary']['equipment_count']}")
        
        print("\n  Failures by equipment:")
        for eq in result['summary']['by_equipment']:
            print(f"    - {eq['equipment_name']}: {eq['failure_count']} failures")
    else:
        print(f"\n❌ Failed to get report: {result.get('message')}")


def test_invalid_duration():
    """Test invalid duration format"""
    print("\n" + "=" * 60)
    print("Testing Invalid Duration Format...")
    print("=" * 60)
    
    url = f"{API_BASE}/equipment-failure"
    
    # Invalid duration format
    payload = {
        "equipment_code": "PLC01",
        "description": "Test invalid duration",
        "duration": "25:00"  # Invalid: hour > 23
    }
    
    print("\nPayload with invalid duration:")
    print(json.dumps(payload, indent=2))
    
    response = session.post(url, json=payload)
    result = response.json()
    
    print("\nResponse:")
    print(json.dumps(result, indent=2))
    
    if result.get('status') == 'error':
        print(f"\n✓ Validation working correctly: {result.get('message')}")
    else:
        print(f"\n❌ Validation should have caught this error")


def main():
    """Main test execution"""
    try:
        # Authenticate
        authenticate()
        
        # Test 1: Create with duration
        create_equipment_failure_with_duration()
        
        # Test 2: Create without duration
        create_equipment_failure_without_duration()
        
        # Test 3: Get failures list
        get_equipment_failures()
        
        # Test 4: Get failure report
        get_equipment_failure_report()
        
        # Test 5: Test invalid duration
        test_invalid_duration()
        
        print("\n" + "=" * 60)
        print("✓ All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
