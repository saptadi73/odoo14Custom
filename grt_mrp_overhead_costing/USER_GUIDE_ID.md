# Quick Guide GRT MRP Overhead Costing

Panduan singkat ini ditujukan untuk user finance, cost accounting, dan operasional agar bisa menjalankan modul tanpa harus membaca dokumentasi teknis yang panjang.

## Tujuan

Modul ini dipakai untuk:

- memasukkan overhead listrik dan SDM ke cost produksi
- menghitung tarif overhead per kg atau per batch
- membandingkan actual overhead dengan absorbed overhead
- membuat jurnal adjustment tanpa double pembiayaan

## Menu Utama

Gunakan menu berikut:

- `Manufacturing > Overhead Periods`
- `Manufacturing > Configuration > Overhead Types`

## Alur Kerja Paling Sederhana

### 1. Cek Overhead Type

Pastikan minimal ada:

- `Listrik Produksi`
- `SDM Produksi`

Cek field berikut:

- `Allocation Basis`
- `Default Source Expense Account`
- `Absorption Account`
- `Variance Account`

Untuk kondisi saat ini, basis yang disarankan:

- `Listrik Produksi` = `Per Kg`
- `SDM Produksi` = `Per Kg`

## 2. Buat Overhead Period

Masuk ke `Manufacturing > Overhead Periods`, lalu buat periode bulanan.

Contoh:

- `01/02/2026 - 28/02/2026`

Isi:

- `Adjustment Journal`

Lalu klik:

- `Init Types`

## 3. Isi Actual Overhead

Ada 2 cara paling praktis:

### Cara A. Dari Expense atau Journal

- Tandai expense/jurnal dengan `MRP Overhead Type`
- Klik `Load Source Entries`

### Cara B. Input Manual

Kalau actual belum siap dari jurnal, isi:

- `Manual Actual Amount`

Contoh:

- Listrik = `9.000.000`
- SDM = `6.300.000`

## 4. Hitung Overhead

Klik:

- `Compute Overhead`

Yang perlu dicek:

- `Basis Qty`
- `Rate`
- `Absorbed Amount`
- `Variance Amount`

## 5. Buat Jurnal Adjustment

Klik:

- `Create Adjustment`

Jurnal akan dibuat dalam status `draft`.

Review dulu, lalu post jika sudah benar.

## Contoh Perhitungan

Misal:

- Actual listrik = `Rp 9.000.000`
- Total produksi bulan itu = `9.000 kg`

Maka:

```text
Tarif listrik = 9.000.000 / 9.000 = 1.000 per kg
```

Kalau satu MO menghasilkan `1.000 kg`, maka overhead listrik MO itu:

```text
1.000 x 1.000 = 1.000.000
```

## Cek Cepat Sebelum Posting Jurnal

Pastikan:

- semua line overhead sudah benar
- actual amount sudah sesuai
- basis qty masuk akal
- variance sudah dipahami
- jurnal adjustment masih draft dan sudah direview

## Jika Ada Masalah

### Basis Qty = 0

Periksa:

- apakah ada MO done pada periode itu
- apakah basis overhead sudah benar

### Actual Amount = 0

Periksa:

- apakah expense/jurnal sudah ditag
- apakah `Manual Actual Amount` sudah diisi
- apakah sudah klik `Load Source Entries`

### Variance terlalu besar

Periksa:

- actual overhead belum lengkap
- expense belum ditag
- basis alokasi salah
- tarif manual tidak sesuai

## Rekomendasi Pemakaian Awal

Untuk masa awal implementasi:

1. pakai basis `Per Kg`
2. isi actual dengan `Manual Actual Amount` dulu
3. setelah hasil valid, baru disiplinkan tagging expense dan journal
