#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script untuk check product_tmpl_id menggunakan SCADA API
Berguna untuk manual weighing di grt_scada
"""

import requests
import json
import sys
from datetime import datetime

# Konfigurasi
URL = 'http://localhost:8069'
DB = 'rimang'
USERNAME = 'admin'
PASSWORD = 'admin'

def print_header(title):
    """Print header dengan garis"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def print_table_header():
    """Print header tabel produk"""
    print(f"\n{'ID':<8} {'Tmpl ID':<10} {'Nama Produk':<40} {'Kategori':<20}")
    print("-" * 80)

def print_product_row(product):
    """Print satu baris data produk"""
    prod_id = str(product.get('product_id', '-'))
    tmpl_id = str(product.get('product_tmpl_id', '-'))
    name = product.get('product_name', '-')[:38]
    category = product.get('product_category', '-')[:18]
    print(f"{prod_id:<8} {tmpl_id:<10} {name:<40} {category:<20}")

def authenticate():
    """Login ke Odoo dan dapatkan session cookie"""
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Authenticating...")
        
        session = requests.Session()
        
        # Login
        login_url = f'{URL}/web/session/authenticate'
        login_data = {
            'jsonrpc': '2.0',
            'params': {
                'db': DB,
                'login': USERNAME,
                'password': PASSWORD
            }
        }
        
        response = session.post(login_url, json=login_data)
        response.raise_for_status()
        
        result = response.json()
        if result.get('result') and result['result'].get('uid'):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Authenticated successfully")
            return session
        else:
            print("ERROR: Authentication failed")
            print(json.dumps(result, indent=2))
            return None
            
    except Exception as e:
        print(f"ERROR during authentication: {str(e)}")
        return None

def get_products_via_api(session, category_name=None):
    """
    Get list produk menggunakan SCADA API endpoint
    """
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching products from SCADA API...")
        
        # Build request
        api_url = f'{URL}/api/scada/products'
        
        # Use JSON-RPC POST method
        data = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'limit': 100,
                'active': True
            }
        }
        
        if category_name:
            data['params']['category_name'] = category_name
        
        response = session.post(api_url, json=data)
        response.raise_for_status()
        
        result = response.json()
        
        # Check if result is a list (successful response)
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and 'result' in result:
            return result['result']
        else:
            print("ERROR: Unexpected response format")
            print(json.dumps(result, indent=2))
            return None
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print_header("CHECK PRODUCT TEMPLATE ID via SCADA API")
    
    # Get optional category filter from command line
    category_filter = None
    if len(sys.argv) > 1:
        category_filter = sys.argv[1]
        print(f"\nFilter kategori: {category_filter}")
    
    # Authenticate
    session = authenticate()
    if not session:
        print("\nAuthentication gagal. Program dihentikan.")
        return
    
    # Get products
    products = get_products_via_api(session, category_name=category_filter)
    
    if not products:
        print("\nTidak ada data produk atau terjadi error.")
        return
    
    # Display results
    print(f"\nTotal produk ditemukan: {len(products)}")
    print_table_header()
    
    for product in products:
        print_product_row(product)
    
    print("\n" + "=" * 80)
    print("CATATAN:")
    print("- product_id: ID variant produk (product.product)")
    print("- product_tmpl_id: ID template produk (product.template)")
    print()
    print("UNTUK MANUAL WEIGHING/CONSUMPTION:")
    print("- Gunakan product_id untuk field 'material_id' di scada.material.consumption")
    print("- API /api/scada/mo/manual-consumption accept product_id atau product_tmpl_id")
    print("- Jika kirim product_tmpl_id, system akan otomatis ambil variant pertama")
    print("=" * 80)
    print("\nCara penggunaan:")
    print(f"  python {sys.argv[0]}                    # Semua produk")
    print(f"  python {sys.argv[0]} 'Raw'              # Filter kategori Raw")
    print(f"  python {sys.argv[0]} 'Finished'         # Filter kategori Finished")
    print("=" * 80 + "\n")

if __name__ == '__main__':
    main()
