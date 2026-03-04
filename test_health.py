#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test a working endpoint to verify API is responsive
"""
import requests

API_URL = 'http://localhost:8070'

print("Testing http://localhost:8070/api/scada/health endpoint...")

try:
    r = requests.get(f'{API_URL}/api/scada/health')
    
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
    
    if r.status_code == 200:
        print("\n✓ API health endpoint works!")
        
        # Now test mo-list-detailed
        print("\nTesting /api/scada/mo-list-detailed endpoint...")
        
        session = requests.Session()
        r = session.post(
            f'{API_URL}/api/scada/mo-list-detailed',
            json={'params': {'limit': 10}}
        )
        
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:500]}")
    else:
        print(f"\n❌ Health check failed with status {r.status_code}")

except Exception as e:
    print(f"Error: {e}")
