# Product Label Guide

Panduan ini menjelaskan cara cetak label produk menggunakan modul `garazd_product_label`, termasuk:
- Cetak label dari Product
- Cetak label dari Lot/Serial Number
- Cetak label bulk per batch Manufacturing Order (MO)

## 1. Prasyarat

- Modul `garazd_product_label` sudah ter-install/upgrade.
- Modul dependensi aktif:
  - `product`
  - `stock`
  - `mrp`
- User memiliki hak akses untuk Product/Inventory/Manufacturing sesuai kebutuhan.

## 2. Alur Cetak Label

### A. Cetak dari Product

Gunakan saat ingin cetak label berdasarkan daftar produk.

Langkah:
1. Buka daftar Product (`product.template` atau `product.product`).
2. Pilih satu atau beberapa product.
3. Klik `Print > Custom Product Labels`.
4. Atur qty label, template, dan opsi.
5. Klik `Print` atau `Preview`.

### B. Cetak dari Lot/Serial Number

Gunakan saat ingin label menampilkan nomor lot/serial hasil produksi.

Langkah:
1. Buka `Inventory > Lots/Serial Numbers`.
2. Pilih satu atau beberapa lot/serial.
3. Klik `Print > Custom Product Labels`.
4. Wizard otomatis mengisi:
   - Product
   - Lot/Serial Number
   - Qty default = 1
5. Klik `Print`.

Perilaku label:
- Jika ada `lot_id`, label menampilkan teks `LOT: <nomor_lot>`.
- Barcode label menggunakan nilai lot/serial (`Code128`).

### C. Cetak Bulk per Batch (Manufacturing Order)

Gunakan untuk cetak massal satu batch produksi.

Langkah:
1. Buka `Manufacturing > Operations > Manufacturing Orders`.
2. Pilih satu atau beberapa MO.
3. Klik `Print > Custom Product Labels (Batch)`.
4. Wizard otomatis membuat label line dari finished product batch:
   - Jika finished move line punya lot/serial: dibuat label per lot/serial.
   - Qty label mengikuti `qty_done` (integer, minimum 1).
   - Fallback: jika belum ada lot move line, qty ambil dari `qty_producing` atau `product_qty`.
5. Review, lalu klik `Print`.

## 3. Opsi pada Wizard

- `Label`: pilih format label (mis. 57x35, 50x38, custom template).
- `Label quantity per product`: set qty massal.
- `Set quantity`: menerapkan qty ke semua line.
- `Preview`: preview sebelum print.
- `Human readable barcode`: tampilkan teks barcode di label.
- `Border`: ketebalan border label.

## 4. Tips Operasional

- Untuk akurasi traceability, cetak dari menu Lot/Serial atau dari MO batch yang sudah selesai.
- Jika menggunakan scanner, pertahankan format barcode `Code128` untuk lot/serial alfanumerik.
- Gunakan `Preview` sebelum cetak banyak agar layout kertas sesuai.

## 5. Troubleshooting

### Tidak muncul menu Print di Lot/Serial atau MO
- Pastikan modul `garazd_product_label` sudah di-upgrade setelah perubahan terakhir.
- Pastikan user punya akses ke model terkait (`stock.production.lot`, `mrp.production`).

### Nomor lot tidak muncul di label
- Pastikan label line memiliki `lot_id`.
- Untuk batch print MO, pastikan finished move line sudah memiliki lot/serial dan `qty_done > 0`.

### Barcode kosong
- Jika print dari lot/serial, barcode memakai `lot.name`.
- Jika print dari product tanpa lot, barcode memakai `product.barcode`.

## 6. Catatan Teknis (Implementasi)

Fitur ini diimplementasikan pada:
- `garazd_product_label/wizard/print_product_label.py`
- `garazd_product_label/wizard/print_product_label_line.py`
- `garazd_product_label/wizard/print_product_label_views.xml`
- `garazd_product_label/report/product_label_templates.xml`
- `garazd_product_label/__manifest__.py`

