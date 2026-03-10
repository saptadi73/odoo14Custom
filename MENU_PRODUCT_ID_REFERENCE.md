# Menu Product ID Reference (SCADA) - User Guide

## Overview

Menu baru telah ditambahkan di **Inventory** untuk memudahkan melihat **product_id** dan **product_tmpl_id** langsung dari UI Odoo. Menu ini sangat berguna untuk reference saat melakukan **manual weighing** atau **manual consumption** di SCADA.

---

## Lokasi Menu

**Navigasi:**
```
Inventory > Products > Product ID Reference (SCADA)
```

**Path lengkap:**
- Klik menu **Inventory** (atau Stock)
- Hover/klik **Products**
- Klik **Product ID Reference (SCADA)**

---

## Fitur View

### Kolom yang Ditampilkan:

| Kolom | Deskripsi | Penggunaan |
|-------|-----------|------------|
| **product_id** | ID variant produk | Untuk field `material_id` di consumption |
| **product_tmpl_id** | ID template produk | Untuk BoM lookup atau API fallback |
| **Internal Reference** | Kode internal produk | Reference tambahan |
| **Product Name** | Nama produk | Identifikasi produk |
| **Category** | Kategori produk | Grouping/filter |
| **Type** | Tipe produk | Stockable/Consumable/Service |
| **UoM** | Unit of Measure | Satuan produk |

### Filter Default:
- ✅ **Active only** (hanya produk aktif)
- ✅ **Stockable products** (produk type='product')

### Filter Tambahan:
- Filter by product_id
- Filter by product_tmpl_id
- Filter by product name
- Filter by internal reference
- Filter by category
- Filter by type (Stockable/Consumable/Service)
- Show archived products

### Group By:
- Category
- Product Type

---

## Cara Penggunaan

### 1. Cari Product ID untuk Manual Weighing

**Langkah:**
1. Buka menu **Inventory > Products > Product ID Reference (SCADA)**
2. Gunakan search box untuk cari produk (by name/code)
3. Catat **product_id** dan **product_tmpl_id** dari kolom pertama dan kedua
4. Gunakan ID tersebut saat create manual consumption

**Example:**
```
product_id: 101
product_tmpl_id: 50
Product Name: Jagung Giling
Category: Raw Material
```

### 2. Filter by Category

**Langkah:**
1. Buka menu
2. Klik icon filter (🔍)
3. Ketik nama kategori di search box
4. Atau gunakan "Group By > Category" untuk grouping

**Example:**
- Cari produk kategori "Raw Material"
- Cari produk kategori "Finished Goods"

### 3. Copy ID untuk API Request

**Langkah:**
1. Buka menu
2. Cari produk yang diinginkan
3. Copy product_id atau product_tmpl_id
4. Gunakan di API request manual consumption

**Example API call:**
```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "mo_id": 10,
    "consumptions": [
      {
        "product_id": 101,
        "quantity": 50.0
      }
    ]
  }
}
```

---

## Keuntungan Menu Ini

### ✅ Mudah Diakses
- Langsung dari menu Inventory
- Tidak perlu buka developer mode
- Tidak perlu query database

### ✅ Read-Only View
- Tidak bisa edit/delete dari view ini
- Menghindari kesalahan modifikasi data
- Safe untuk semua user

### ✅ Filter Lengkap
- Default filter: active + stockable
- Bisa filter by category
- Bisa group by type

### ✅ Clean Display
- Hanya menampilkan kolom penting
- product_id dan product_tmpl_id di kolom depan
- Easy to read dan copy

---

## Integrasi dengan Script

Menu ini **complement** dengan script yang sudah ada:

### Script Python untuk Bulk Check:
```bash
# CLI check
python check_product_tmpl_id.py
python check_product_tmpl_id_api.py "Raw"
```

### Menu UI untuk Quick Reference:
- Buka **Inventory > Products > Product ID Reference (SCADA)**
- Visual dan interactive
- Filter real-time

---

## Troubleshooting

### Menu tidak muncul?
**Solusi:**
1. Upgrade module grt_scada:
   ```bash
   python upgrade_scada_module.py
   ```
2. Refresh browser (Ctrl+F5)
3. Logout dan login kembali

### Kolom product_tmpl_id tidak terlihat?
**Solusi:**
- Kolom sudah visible by default
- Kalau hilang, klik icon kolom (☰) dan centang "product_tmpl_id"

### Filter tidak bekerja?
**Solusi:**
- Clear filter dan coba lagi
- Pastikan tidak ada filter conflict
- Reset view: klik "Reset" di search bar

---

## Security & Access Rights

### Siapa yang bisa akses?
- User dengan access rights ke **Inventory/Products**
- User dengan group **Stock User** atau lebih tinggi
- SCADA API user (kalau perlu reference visual)

### Restriction:
- ❌ Tidak bisa create produk baru dari view ini
- ❌ Tidak bisa edit produk dari view ini
- ❌ Tidak bisa delete produk dari view ini
- ✅ Hanya bisa view/read

---

## Tips & Best Practices

### 1. Bookmark Menu
- Tambahkan ke browser bookmark untuk quick access
- URL: `http://localhost:8069/web#menu_id=XXX&action=XXX`

### 2. Gunakan Search dengan Smart
- Search by product name: ketik nama produk
- Search by ID: ketik angka ID langsung
- Search by code: ketik internal reference

### 3. Export untuk Documentation
- Bisa export list ke Excel/CSV kalau perlu
- Klik "Export" di pojok kanan atas
- Pilih kolom yang mau di-export

### 4. Combine dengan Script
- Gunakan menu UI untuk quick check 1-2 produk
- Gunakan script Python untuk bulk check many products
- Gunakan API untuk programmatic access

---

## Update History

**Version 7.0.85 - 2026-03-10**
- ✅ Added dedicated tree view for product ID reference
- ✅ Added search view with filters
- ✅ Added menu item under Inventory > Products
- ✅ Default filter: active + stockable products
- ✅ Read-only view for safety

---

## Related Documentation

- [PANDUAN_PRODUCT_TMPL_ID_MANUAL_WEIGHING.md](PANDUAN_PRODUCT_TMPL_ID_MANUAL_WEIGHING.md) - Panduan lengkap penggunaan product_id dan product_tmpl_id
- [check_product_tmpl_id.py](check_product_tmpl_id.py) - Script CLI untuk check via XML-RPC
- [check_product_tmpl_id_api.py](check_product_tmpl_id_api.py) - Script CLI untuk check via SCADA API
- [grt_scada/API_SPEC.md](grt_scada/API_SPEC.md) - API documentation

---

**Module:** grt_scada v7.0.85  
**Author:** PT Gagak Rimang Teknologi  
**Date:** 2026-03-10
