# Panduan Ringkas User Operasional CRM Business Category

## Tujuan
Panduan ini untuk user harian agar paham cara kerja CRM berdasarkan Business Category tanpa detail teknis.

## Menu yang Dipakai
1. `CRM > Configuration > Business Categories`
- Dipakai admin untuk membuat/mengelola kategori bisnis.

2. `CRM > Configuration > Pipelines by Category`
- Dipakai admin untuk membuat pipeline (Sales Team) dan menentukan Business Category untuk tiap pipeline.

3. `CRM > Configuration > User Category Access`
- Dipakai admin untuk mengatur kategori yang boleh diakses tiap user.

## Aturan Utama
1. Setiap pipeline harus punya Business Category.
2. Opportunity/Lead harus sesuai kategori pipeline yang dipilih.
3. User biasa hanya bisa melihat data sesuai kategori yang diizinkan.
4. User biasa tidak bisa update data user lain.
5. Admin/Manager CRM bisa melihat dan mengubah semua data.

## Cara Setup (Admin)
1. Buat kategori di `Business Categories`.
2. Buat/ubah pipeline di `Pipelines by Category` dan isi field `Business Category`.
3. Buka `User Category Access`, lalu isi per user:
- `Allowed Business Categories`
- `Default Business Category`
- `Active Business Category`

## Cara Pakai Harian (User Sales)
1. Buka CRM Pipeline.
2. Saat membuat lead/opportunity, pilih Sales Team/pipeline sesuai pekerjaan.
3. Sistem akan menjaga agar kategori lead sesuai kategori pipeline.

## Troubleshooting Cepat
1. Tidak bisa lihat data tim lain:
- Kemungkinan kategori belum di-allow untuk user.

2. Tidak bisa edit data tertentu:
- User biasa hanya bisa edit data milik sendiri (dalam kategori yang diizinkan).

3. Menu `Pipelines by Category`/`User Category Access` tidak muncul:
- Pastikan user punya hak admin/manager yang sesuai.
- Refresh browser (`Ctrl+F5`) atau login ulang.

## Siapa Menghubungi Jika Ada Masalah
Hubungi admin ERP/IT internal untuk perubahan akses kategori dan hak update data.
