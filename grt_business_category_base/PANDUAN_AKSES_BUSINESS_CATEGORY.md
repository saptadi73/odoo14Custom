# Panduan Akses Business Category

## 1. Tujuan
Dokumen ini menjelaskan cara mengatur akses `Business Category` pada user setelah master category dipindahkan ke modul induk `grt_business_category_base`.

## 2. Lokasi Pengaturan

### 2.1 Master Business Category
Menu:
- `Settings > Administration > Business Categories`

Fungsi:
- Membuat category induk yang akan dipakai bersama oleh CRM, Sales, Purchase, Expense, dan Inventory.

### 2.2 Akses User per Business Category
Menu:
- `Settings > Administration > User Category Access`

Alternatif:
- `Settings > Users & Companies > Users > tab Business Category Access`

## 3. Arti Setiap Field

### 3.1 Allowed Business Categories
Ini adalah daftar category yang **secara manual diizinkan** untuk diakses oleh user.

Fungsi:
- Menentukan category mana yang boleh dipakai user.
- Menjadi dasar utama agar category muncul di pilihan `Default` dan `Active`.

Catatan:
- Jika category belum ada di field ini, biasanya category tidak akan muncul di dropdown `Default Business Category` dan `Active Business Category`.

### 3.2 Team Business Categories
Ini adalah daftar category yang didapat **otomatis** dari membership user di team, misalnya:
- `crm.team`
- `purchase.team`
- `expense.team`
- `stock.team`

Fungsi:
- Menambahkan akses category tanpa harus selalu diisi manual.

Catatan:
- Field ini readonly.
- Nilainya dihitung otomatis oleh sistem.

### 3.3 Effective Business Categories
Ini adalah gabungan dari:
- `Allowed Business Categories`
- `Team Business Categories`

Fungsi:
- Menjadi daftar category final yang benar-benar bisa dipakai user.

Catatan:
- Field ini readonly.
- `Default Business Category` dan `Active Business Category` hanya boleh memilih dari field ini.

### 3.4 Default Business Category
Ini adalah category bawaan saat user membuat record baru.

Contoh:
- Saat user membuat Lead, Sales Order, Purchase Order, Expense, atau Inventory Transfer baru, sistem akan mencoba memakai category default ini bila logic modul menggunakannya.

Aturan:
- Harus termasuk ke `Effective Business Categories`.
- Company dari category harus termasuk ke daftar company user.

### 3.5 Active Business Category
Ini adalah category aktif yang dipakai sebagai konteks kerja user saat ini.

Fungsi:
- Dipakai oleh beberapa default value dan filtering di modul business category.
- Konsepnya mirip seperti active company, tetapi khusus untuk business category.

Aturan:
- Harus termasuk ke `Effective Business Categories`.
- Company dari category harus termasuk ke daftar company user.

## 4. Kenapa Business Category Tidak Muncul di Dropdown
Jika category yang baru dibuat tidak muncul di `Default Business Category` atau `Active Business Category`, biasanya penyebabnya salah satu dari berikut:

1. Category belum dimasukkan ke `Allowed Business Categories`.
2. User belum tergabung di team yang membawa category tersebut.
3. Company pada category tidak termasuk ke `Company` / `Allowed Companies` milik user.
4. `Effective Business Categories` belum ter-refresh.

## 5. Urutan Setting yang Benar
Disarankan mengikuti urutan berikut:

1. Buat dulu master category di menu `Business Categories`.
2. Pastikan `Company` pada category sudah benar.
3. Buka user yang akan diberi akses.
4. Isi `Allowed Business Categories`.
5. Jika perlu, klik tombol `Sync Team Access`.
6. Pastikan category sudah muncul di `Effective Business Categories`.
7. Baru pilih `Default Business Category`.
8. Baru pilih `Active Business Category`.

## 6. Contoh Praktis
Misal dibuat category:
- `Retail`

Lalu user `Anggota A - 1` harus bisa memakai category itu.

Langkah:
1. Buka form user.
2. Tambahkan `Retail` ke `Allowed Business Categories`.
3. Simpan atau tunggu onchange selesai.
4. Cek bahwa `Retail` muncul di `Effective Business Categories`.
5. Pilih `Retail` pada `Default Business Category`.
6. Pilih `Retail` pada `Active Business Category`.

Jika langkah nomor 2 belum dilakukan, maka `Retail` tidak akan muncul di dropdown `Default` dan `Active`.

## 7. Ringkasan Singkat
- `Allowed` = izin manual
- `Team` = izin otomatis dari team
- `Effective` = gabungan final
- `Default` = bawaan saat create record
- `Active` = category aktif untuk konteks user

## 8. Catatan Admin
- Pengaturan ini idealnya dilakukan oleh user dengan hak `System Administrator`.
- Jika menu atau tab tidak terlihat, cek group access user.
- Jika dropdown terasa tidak update, lakukan refresh browser atau buka ulang form user.
