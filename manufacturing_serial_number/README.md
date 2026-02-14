# Manufacturing Serial Number Module

## Deskripsi
Modul ini menyediakan sistem tracking serial number otomatis untuk produk hasil manufacturing di Odoo 14 Community Edition.

## Fitur Utama

### 1. **Auto Generate Serial Number**
   - Serial number unik dibuat otomatis setiap kali Manufacturing Order selesai
   - Format: `PREFIX-SEQUENCE-RANDOMCODE` (contoh: `MFG-S000001-A3X9`)
   - Prefix bisa menggunakan kode produk (Product Reference)

### 2. **Integrasi dengan Manufacturing Order**
   - Checkbox "Auto Generate Serial" di Manufacturing Order
   - Smart button untuk melihat semua serial yang dihasilkan
   - Tab "Serial Numbers" untuk melihat detail serial
   - Button manual "Generate Serials Now" jika perlu

### 3. **Product Configuration**
   - Field "Use Manufacturing Serial" di Product form
   - Smart button untuk melihat history serial per produk
   - Counter jumlah serial yang sudah dihasilkan

### 4. **Serial Number Management**
   - State tracking: Draft → Produced → Delivered → Cancelled
   - Link ke Manufacturing Order
   - Search & filter berdasarkan product, state, date
   - Group by product, MO, state, atau date

### 5. **Security & Access Rights**
   - MRP User: Read, Write, Create
   - MRP Manager: Full access termasuk Delete
   - Stock User: Read only

## Instalasi

1. Copy folder `manufacturing_serial_number` ke direktori addons Odoo
2. Restart Odoo server
3. Aktifkan Developer Mode
4. Update Apps List
5. Cari "Manufacturing Serial Number" dan klik Install

## Cara Penggunaan

### Setup Produk
1. Buka **Inventory > Products**
2. Pilih produk yang ingin di-track
3. Di tab **Inventory**, aktifkan **"Use Manufacturing Serial"**
4. Save

### Menggunakan di Manufacturing
1. Buat Manufacturing Order baru
2. Pastikan checkbox **"Auto Generate Serial"** aktif
3. Process manufacturing order seperti biasa
4. Saat klik **"Mark as Done"**, serial numbers akan dibuat otomatis
5. Lihat serial numbers di Smart Button atau tab "Serial Numbers"

### Manual Generate (Opsional)
Jika serial belum ter-generate:
1. Buka Manufacturing Order yang sudah Done/In Progress
2. Klik tab **"Serial Numbers"**
3. Klik button **"Generate Serials Now"**

### Melihat History Serial
- **Per Product**: Buka Product → klik Smart Button "Mfg Serials"
- **Per MO**: Buka Manufacturing Order → klik Smart Button "Serials"
- **All Serials**: Menu Manufacturing > Manufacturing Serials > Serial Numbers

## Konfigurasi Lanjutan

### Format Serial Number
Edit di file `models/manufacturing_serial.py`, method `_generate_serial_number()`:
```python
def _generate_serial_number(self, product_id=None):
    prefix = 'MFG'  # Ubah prefix default di sini
    # ... rest of code
```

### Batch Size Limit
Default maksimal 1000 serial per MO. Ubah di `models/mrp_production.py`:
```python
if qty_to_generate > 1000:  # Ubah angka ini
    raise UserError(...)
```

## Struktur Data

### Model: manufacturing.serial
- `serial_number`: Nomor serial unik
- `product_id`: Produk yang diproduksi
- `mrp_production_id`: Link ke Manufacturing Order
- `production_date`: Tanggal produksi
- `state`: Status (draft/produced/delivered/cancelled)
- `lot_id`: Link ke Stock Lot (opsional)

## Dependencies
- mrp (Manufacturing)
- stock (Inventory)
- product (Product Management)

## Kompatibilitas
- Odoo 14 Community Edition
- Odoo 14 Enterprise Edition

## Lisensi
LGPL-3

## Support
Untuk pertanyaan atau issue, hubungi tim development.

## Changelog

### Version 14.0.1.0.0 (2026-02-14)
- Initial release
- Auto generate serial numbers
- Manufacturing Order integration
- Product configuration
- Serial management views
