# Panduan Operasional GRT MRP Overhead Costing

Dokumen ini menjelaskan cara memakai modul `grt_mrp_overhead_costing` untuk memasukkan biaya overhead produksi ke cost produksi, merekonsiliasi dengan expense aktual, menghitung variance, dan membuat jurnal adjustment tanpa double pembiayaan.

## 1. Tujuan Modul

Modul ini dipakai untuk kebutuhan berikut:

- Menyimpan overhead bulanan seperti listrik dan SDM.
- Menghitung tarif overhead per basis alokasi.
- Mengalokasikan overhead ke Manufacturing Order (MO) yang sudah selesai.
- Membandingkan actual overhead vs absorbed overhead.
- Menghitung selisih over/under absorption.
- Membuat jurnal adjustment agar expense aktual dan cost produksi tetap sinkron.

## 2. Konsep Dasar

Modul ini memakai konsep **actual overhead** dan **absorbed overhead**.

- `Actual overhead`: biaya overhead yang benar-benar terjadi, biasanya dari expense, jurnal, atau input manual.
- `Absorbed overhead`: biaya overhead yang dibebankan ke produk berdasarkan basis alokasi seperti per kg atau per batch.
- `Variance`: selisih antara actual overhead dan absorbed overhead.

Rumus sederhananya:

```text
Tarif overhead = Actual overhead / Total basis alokasi
Applied overhead per MO = Basis MO x Tarif overhead
Variance = Actual overhead - Total applied overhead
```

## 3. Menu Yang Digunakan

Setelah modul terpasang, menu utama yang dipakai adalah:

- `Manufacturing > Overhead Periods`
- `Manufacturing > Configuration > Overhead Types`

Tambahan field juga muncul di:

- Form `Expense`: field `MRP Overhead Type`
- Form `Manufacturing Order`: ringkasan applied overhead dan detail alokasi overhead
- Form `Journal Entry`: field `MRP Overhead Type` dan `MRP Overhead Period`

## 4. Struktur Data Modul

### 4.1. Overhead Type

Master untuk mendefinisikan jenis overhead.

Contoh:

- `Listrik Produksi`
- `SDM Produksi`

Field penting:

- `Allocation Basis`
  - `Per Kg`: overhead dibagi berdasarkan total kuantitas produksi.
  - `Per Jam`: overhead dibagi berdasarkan total jam kerja. Cocok hanya jika data workorder/duration ada.
  - `Per MO`: overhead dibagi per batch/MO.
- `Default Source Expense Account`
  - Akun sumber expense aktual jika tidak ada journal item yang ditag langsung.
- `Absorption Account`
  - Akun yang didebit ketika overhead dimasukkan ke cost produksi.
- `Variance Account`
  - Akun untuk selisih actual vs absorbed.

### 4.2. Overhead Period

Dokumen bulanan untuk memproses overhead.

Contoh:

- `Overhead 02/2026`
- `Overhead 03/2026`

Field penting:

- `Date Start` dan `Date End`
- `Adjustment Journal`
- `Overhead Lines`
- `Allocations`
- `Actual Amount Total`
- `Absorbed Amount Total`
- `Variance Amount Total`
- `State`
  - `Draft`
  - `Computed`
  - `Adjustment Created`

### 4.3. Overhead Period Line

Baris per jenis overhead dalam satu periode.

Contoh:

- Line `Listrik Produksi`
- Line `SDM Produksi`

Field penting:

- `Allocation Basis`
- `Rate Mode`
  - `Auto`: sistem hitung tarif otomatis dari actual / total basis
  - `Manual`: tarif diisi manual
- `Manual Rate`
- `Manual Actual Amount`
- `Source Journal Items`
- `MO Allocations`
- `Actual Amount`
- `Basis Qty`
- `Rate`
- `Absorbed Amount`
- `Variance Amount`

## 5. Alur Operasional Bulanan

### Langkah 1. Siapkan Overhead Type

Masuk ke:

- `Manufacturing > Configuration > Overhead Types`

Pastikan untuk setiap jenis overhead sudah diisi:

- nama overhead
- basis alokasi
- akun sumber
- akun absorpsi
- akun variance

Contoh konfigurasi yang saat ini cocok dengan kebutuhan Anda:

- `Listrik Produksi`: basis `Per Kg`
- `SDM Produksi`: basis `Per Kg`

Catatan:

- Jika nanti SDM ingin dihitung per batch, ubah basis `SDM Produksi` menjadi `Per MO`.
- Jangan pakai `Per Jam` jika workorder dan durasi produksi tidak tersedia.

### Langkah 2. Buat Overhead Period

Masuk ke:

- `Manufacturing > Overhead Periods`

Buat periode bulanan, misalnya:

- `01/02/2026 - 28/02/2026`

Isi:

- `Adjustment Journal`
  - contoh: `MISC`
- `Note`
  - opsional

Lalu klik:

- `Init Types`

Tujuannya untuk membuat line overhead otomatis dari master `Overhead Types`.

### Langkah 3. Tarik Actual Overhead

Ada 3 cara memasukkan actual overhead:

#### A. Dari Expense

Pada form `Expense`, isi field:

- `MRP Overhead Type`

Contoh:

- expense listrik ditandai sebagai `Listrik Produksi`
- expense gaji tenaga produksi ditandai sebagai `SDM Produksi`

Ketika expense sheet membuat jurnal, jurnal tersebut akan ikut membawa `MRP Overhead Type`.

#### B. Dari Journal Entry

Kalau actual overhead tidak berasal dari expense, Anda bisa input jurnal manual dan isi:

- `MRP Overhead Type`

Contoh:

- jurnal accrual listrik
- jurnal pengakuan beban SDM produksi

#### C. Manual Actual Amount

Kalau actual overhead belum siap dari jurnal/expense, isi `Manual Actual Amount` di line overhead.

Cara ini cocok untuk:

- masa transisi awal
- simulasi perhitungan
- test sistem sebelum disiplin tagging expense diterapkan

### Langkah 4. Load Source Entries

Di form `Overhead Period`, klik:

- `Load Source Entries`

Fungsi tombol ini:

- mengambil journal items posted dalam periode yang punya `MRP Overhead Type` sesuai line overhead
- menempelkan journal items tersebut ke `Source Journal Items`

Jika tidak ada journal item yang cocok, actual overhead tetap bisa berasal dari `Manual Actual Amount`.

### Langkah 5. Compute Overhead

Klik:

- `Compute Overhead`

Fungsi tombol ini:

- mencari MO yang `done` dalam periode
- menghitung total basis alokasi
- menghitung tarif overhead
- membuat baris alokasi overhead per MO
- menghitung absorbed amount dan variance

## 6. Cara Sistem Menghitung Basis

### 6.1. Basis Per Kg

Untuk `Per Kg`, sistem memakai qty produksi MO.

Pada data yang sekarang, basis ini paling aman karena MO selesai sudah ada dan kuantitas produksinya terbaca.

### 6.2. Basis Per MO

Untuk `Per MO`, setiap MO dihitung `1 batch`.

Cocok untuk overhead yang ingin dibagi rata per batch, bukan berdasarkan tonase/berat.

### 6.3. Basis Per Jam

Untuk `Per Jam`, sistem mencoba membaca:

- duration workorder
- duration expected
- atau fallback dari `date_start` dan `date_finished`

Catatan penting:

- Jika tidak ada workorder atau `date_start`, basis jam akan menjadi `0`.
- Karena kondisi database Anda saat ini tidak memiliki workorder, basis jam tidak disarankan.

## 7. Membuat Jurnal Adjustment

Setelah angka actual dan absorbed sudah benar, klik:

- `Create Adjustment`

Sistem akan membuat jurnal adjustment dalam status `draft`.

Pola jurnalnya:

### 7.1. Reverse Actual Overhead

Akun beban overhead aktual dikredit kembali.

Contoh:

```text
Cr 63110080 Listrik
```

### 7.2. Absorbed Overhead

Akun absorpsi overhead didebit.

Contoh:

```text
Dr 51000020 Manufacturing Overhead Applied - Electricity
```

### 7.3. Variance

Kalau actual dan absorbed tidak sama, selisih masuk ke akun variance.

Contoh:

```text
Dr/Cr 51000090 Manufacturing Overhead Variance
```

## 8. Contoh Operasional Nyata

Contoh Februari 2026:

- Total MO done: 9 MO
- Total basis listrik: `9000 kg`
- Actual listrik: `Rp 9.000.000`
- Tarif listrik: `Rp 1.000/kg`

Hasil:

```text
Tarif = 9.000.000 / 9.000 = 1.000 per kg
Applied overhead = 9.000.000
Variance = 0
```

Jurnal adjustment yang terbentuk:

```text
Cr 63110080 Listrik                                9.000.000
Dr 51000020 Manufacturing Overhead Applied         9.000.000
```

## 9. Kapan Pakai Manual Actual Amount

Gunakan `Manual Actual Amount` bila:

- expense belum disiplin ditag ke `MRP Overhead Type`
- actual overhead masih direkap manual oleh finance
- Anda ingin test alur modul dulu sebelum go-live penuh

Jangan gunakan `Manual Actual Amount` kalau actual overhead sudah lengkap dan akurat dari journal items, karena bisa menyebabkan actual menjadi dobel bila tidak dikontrol.

## 10. Kapan Pakai Manual Rate

Gunakan `Manual Rate` bila perusahaan ingin tarif standar, misalnya:

- listrik dibebankan tetap `Rp 950/kg`
- SDM dibebankan tetap `Rp 700/kg`

Pada mode `Manual`, sistem:

- tetap menghitung basis MO
- tetapi tarif diambil dari `Manual Rate`
- absorbed amount dihitung dari basis x manual rate
- variance = actual - absorbed

## 11. Cara Menghindari Double Pembiayaan

Prinsip pengendaliannya adalah:

- actual overhead tetap dicatat di expense/jurnal aktual
- absorbed overhead dipindahkan ke akun absorpsi melalui jurnal adjustment
- variance dipisahkan ke akun variance

Agar aman:

- gunakan akun beban aktual yang jelas untuk overhead
- gunakan akun absorpsi yang terpisah dari akun beban aktual
- gunakan akun variance yang terpisah
- jangan campur jurnal actual dan absorbed di akun yang sama tanpa kontrol

## 12. Rekomendasi Setup Untuk Kondisi Anda Saat Ini

Karena saat ini data workorder/jam kerja belum tersedia, setup yang disarankan adalah:

- `Listrik Produksi` = `Per Kg`
- `SDM Produksi` = `Per Kg`

Alternatif:

- jika SDM ingin dihitung per batch, ubah `SDM Produksi` menjadi `Per MO`

## 13. Checklist Operasional Bulanan

Gunakan checklist ini setiap akhir bulan:

1. Pastikan semua expense/jurnal overhead sudah masuk.
2. Pastikan expense overhead sudah diberi `MRP Overhead Type`.
3. Buat atau buka `Overhead Period` bulan terkait.
4. Klik `Load Source Entries`.
5. Review `Source Journal Items`.
6. Isi `Manual Actual Amount` jika ada biaya yang belum masuk jurnal.
7. Klik `Compute Overhead`.
8. Review `Basis Qty`, `Rate`, `Absorbed Amount`, dan `Variance Amount`.
9. Klik `Create Adjustment`.
10. Review jurnal draft.
11. Post jurnal adjustment jika sudah benar.

## 14. Troubleshooting

### Kasus 1. Basis Qty = 0

Penyebab umum:

- tidak ada MO done dalam periode
- basis `Per Jam` tetapi workorder/duration tidak ada

Solusi:

- cek tanggal periode
- cek status MO harus `done`
- ubah basis ke `Per Kg` atau `Per MO`

### Kasus 2. Actual Amount = 0

Penyebab umum:

- tidak ada expense/jurnal yang ditag `MRP Overhead Type`
- belum klik `Load Source Entries`
- actual masih belum diinput manual

Solusi:

- tag expense/jurnal dengan overhead type yang benar
- klik `Load Source Entries`
- isi `Manual Actual Amount` bila perlu

### Kasus 3. Jurnal Adjustment Tidak Bisa Dibuat

Penyebab umum:

- akun source/absorption/variance belum lengkap
- line overhead bernilai nol semua

Solusi:

- cek konfigurasi akun di `Overhead Type`
- pastikan ada actual atau absorbed amount

### Kasus 4. Variance Terlalu Besar

Penyebab umum:

- actual overhead belum lengkap
- basis alokasi salah
- ada expense yang belum ditag
- rate manual terlalu tinggi/rendah

Solusi:

- review source journal items
- cek basis alokasi
- cek expense tagging
- bandingkan actual vs absorbed per line overhead

## 15. Saran Implementasi Bertahap

Agar modul ini mudah diadopsi, lakukan bertahap:

### Tahap 1

- gunakan `Manual Actual Amount`
- basis listrik dan SDM = `Per Kg`
- validasi hasil perhitungan dan jurnal

### Tahap 2

- mulai disiplin tagging `Expense` dan `Journal Entry` dengan `MRP Overhead Type`
- kurangi ketergantungan pada input manual

### Tahap 3

- jika diperlukan, pisahkan SDM per batch atau per pusat biaya
- tambahkan governance review bulanan untuk variance

## 16. Ringkasan Singkat

Jika ingin operasional paling sederhana saat ini, lakukan seperti ini:

1. Buat `Overhead Period` bulanan.
2. Pastikan line `Listrik Produksi` dan `SDM Produksi` ada.
3. Isi actual cost dari expense/jurnal atau `Manual Actual Amount`.
4. Klik `Compute Overhead`.
5. Review hasil per kg.
6. Klik `Create Adjustment`.
7. Post jurnal setelah diperiksa finance.

## 17. File Teknis Terkait

Jika ingin melihat source code modul:

- `grt_mrp_overhead_costing/__manifest__.py`
- `grt_mrp_overhead_costing/models/mrp_overhead_period.py`
- `grt_mrp_overhead_costing/models/mrp_overhead_type.py`
- `grt_mrp_overhead_costing/models/hr_expense.py`
- `grt_mrp_overhead_costing/models/account_move.py`
- `grt_mrp_overhead_costing/views/mrp_overhead_period_views.xml`

---

Dokumen ini dibuat untuk kebutuhan operasional dan pembelajaran user internal. Jika alur bisnis berubah, misalnya SDM berganti dari `Per Kg` menjadi `Per MO`, dokumentasi ini sebaiknya ikut diperbarui.
