# GRT Business Category Base

## Ringkasan
`grt_business_category_base` adalah modul induk untuk master `Business Category` yang dipakai bersama oleh:
- CRM
- Sales
- Purchase
- Expense
- Inventory

Modul ini menjadi sumber referensi bersama untuk:
- master `crm.business.category`
- akses category per user
- default/active business category user
- mixin reusable untuk modul lain
- shared `analytic account` pada level business category

## Tujuan
Sebelumnya master `Business Category` menempel ke modul CRM. Setelah refactor, master dipindahkan ke modul base agar:
- pembuatan category cukup satu kali
- semua modul bisa merefer ke category yang sama
- `analytic account` menjadi referensi bersama
- team tetap bisa dikelola per modul

## Menu Utama

### Master Category
Lokasi:
- `Settings > Administration > Business Categories`

Fungsi:
- membuat dan mengelola category induk
- mengatur shared `Analytic Account` untuk category tersebut

### Akses User
Lokasi:
- `Settings > Administration > User Category Access`

Alternatif:
- `Settings > Users & Companies > Users > tab Business Category Access`

Fungsi:
- mengatur category mana yang boleh diakses user
- memilih `Default Business Category`
- memilih `Active Business Category`

## Struktur Konsep
- `Allowed Business Categories`: izin manual untuk user
- `Team Business Categories`: izin otomatis dari membership team
- `Effective Business Categories`: gabungan final dari allowed + team
- `Default Business Category`: category bawaan saat create record
- `Active Business Category`: category aktif sebagai konteks kerja user

## Urutan Setting yang Disarankan
1. Buat master category di menu `Business Categories`
2. Pastikan `Company` category benar
3. Buka form user
4. Isi `Allowed Business Categories`
5. Klik `Sync Team Access` jika diperlukan
6. Pastikan category muncul di `Effective Business Categories`
7. Pilih `Default Business Category`
8. Pilih `Active Business Category`

## Catatan Penting
- `Default` dan `Active` tidak menampilkan semua category
- kedua field itu hanya menampilkan category yang sudah masuk `Effective Business Categories`
- jika category baru tidak muncul di dropdown, biasanya category tersebut belum masuk `Allowed Business Categories` atau company user tidak cocok

## Dokumen Detail
Panduan operasional lengkap tersedia di:

- [PANDUAN_AKSES_BUSINESS_CATEGORY.md](./PANDUAN_AKSES_BUSINESS_CATEGORY.md)
