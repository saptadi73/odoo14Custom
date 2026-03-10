#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script untuk check product_tmpl_id dari produk
Berguna untuk manual weighing di grt_scada
"""

import xmlrpc.client
import sys
from datetime import datetime

# Konfigurasi koneksi Odoo
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

def get_products_with_xmlrpc(category_name=None):
    """
    Get list produk menggunakan XML-RPC melalui common login + execute
    """
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Connecting to Odoo...")
        
        # Authenticate
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        
        if not uid:
            print("ERROR: Authentication failed!")
            return None
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Authenticated as user ID: {uid}")
        
        # Prepare domain filter
        domain = []
        if category_name:
            domain.append(['categ_id.name', 'ilike', category_name])
        
        # Execute search_read
        models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
        products = models.execute_kw(
            DB, uid, PASSWORD,
            'product.product', 'search_read',
            [domain],
            {
                'fields': ['id', 'name', 'product_tmpl_id', 'categ_id', 'type'],
                'limit': 100,
                'order': 'name'
            }
        )
        
        # Transform to match API format
        result = []
        for p in products:
            result.append({
                'product_id': p['id'],
                'product_name': p['name'],
                'product_tmpl_id': p['product_tmpl_id'][0] if p.get('product_tmpl_id') else None,
                'product_category': p['categ_id'][1] if p.get('categ_id') else None,
                'product_type': p.get('type'),
            })
        
        return result
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print_header("CHECK PRODUCT TEMPLATE ID - GRTSCADA Manual Weighing")
    
    # Get optional category filter from command line
    category_filter = None
    if len(sys.argv) > 1:
        category_filter = sys.argv[1]
        print(f"\nFilter kategori: {category_filter}")
    
    # Get products
    products = get_products_with_xmlrpc(category_name=category_filter)
    
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
    print("- product_id: digunakan untuk create consumption record")
    print("- product_tmpl_id: digunakan untuk lookup BoM (BoM biasanya defined di template level)")
    print("- Untuk manual weighing, gunakan product_id atau product_tmpl_id tergantung kebutuhan")
    print("=" * 80)
    print("\nCara penggunaan:")
    print(f"  python {sys.argv[0]}                    # Semua produk")
    print(f"  python {sys.argv[0]} 'Raw'              # Filter kategori Raw")
    print(f"  python {sys.argv[0]} 'Finished'         # Filter kategori Finished")
    print("=" * 80 + "\n")

if __name__ == '__main__':
    main()
