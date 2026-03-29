# PSAK 69 Fit-Gap

## Tujuan
Dokumen ini memetakan tingkat kesesuaian modul `grt_asset_dairy_management` terhadap prinsip-prinsip utama PSAK 69 Agrikultur. Dokumen ini bukan opini audit atau opini akuntansi formal, tetapi alat bantu implementasi agar tim bisnis, finance, dan developer memahami area yang sudah tertutup dan area yang masih memerlukan kebijakan perusahaan.

## Status Ringkas
Penilaian saat ini:
- `Traceability`: kuat untuk alur operasional utama
- `Inventory Link`: sudah terpenuhi untuk pakan dan input medis berbasis stok dengan alur dua tahap
- `PSAK 69 full compliance`: belum sepenuhnya, masih hybrid antara biaya historis, kapitalisasi, fixed asset, dan fair value monitoring

## Prinsip Yang Sudah Cukup Tertutup
### 1. Traceability perubahan nilai
Status: `Fit`

Yang sudah tersedia:
- pakan menghasilkan stock move dan jurnal
- distribusi stok medis ke tas petugas menghasilkan stock move internal
- vitamin dan inseminasi menghasilkan jurnal
- vitamin dan inseminasi berbasis stok menghasilkan stock move dari tas ke lokasi konsumsi medis
- transaksi distribusi medis yang dibatalkan membuat reverse stock move
- transaksi treatment yang dibatalkan membuat reverse stock move dan reverse journal
- reklasifikasi saat mulai produksi menghasilkan jurnal tersendiri
- penyusutan asset produksi menghasilkan jurnal periodik dari engine asset
- CHKPN menghasilkan jurnal impairment atau reversal
- histori status, melahirkan, valuasi, harga daging, serta laporan saldo/mutasi tas tersedia

Implikasi:
- perubahan nilai dan pergerakan stok pada alur utama dapat ditelusuri tanpa menghapus transaksi yang sudah diposting
- audit trail lebih kuat karena koreksi dilakukan melalui reversal, bukan edit diam-diam pada transaksi posted

### 2. Inventory link untuk input biologis utama
Status: `Fit dengan batasan`

Yang sudah tersedia:
- pakan memotong stok riil melalui `stock.move`
- vitamin dan inseminasi berbasis stok memakai alur dua tahap:
  - `Gudang Medis -> Tas Petugas`
  - `Tas Petugas -> Konsumsi ke Sapi`
- tersedia report `Saldo Stok Tas` dan `Mutasi Stok Tas` untuk kontrol stok lapangan
- pembatalan transaksi medis posted sudah memiliki reverse stock move otomatis

Batasan yang masih ada:
- jika produk inseminasi diset sebagai `service`, tidak ada stock move karena secara desain diperlakukan sebagai jasa
- validasi stok tas saat ini memakai `stock.quant` total, belum memperhitungkan reserved quantity secara detail

Catatan:
- untuk banyak implementasi, inseminasi memang lebih tepat diperlakukan sebagai jasa. Karena itu, tidak semua kasus inseminasi perlu inventory link.

### 3. Pemisahan fase pra-produksi dan pasca-produksi
Status: `Fit`

Yang sudah tersedia:
- sebelum melahirkan, biaya pakan, vitamin, dan inseminasi dikapitalisasi ke asset biologis belum produksi
- sesudah melahirkan, biaya operasional diposting sebagai expense
- saat mulai produksi, biaya pra-produksi direklasifikasi ke asset produksi

Nilai tambah:
- alur ini memberi pemisahan treatment akuntansi yang jelas secara operasional

### 4. Kontrol koreksi transaksi
Status: `Fit sebagian`

Yang sudah tersedia:
- distribusi medis posted yang di-cancel akan membuat reverse stock move
- treatment posted yang di-cancel akan membuat reverse stock move dan reverse journal

Gap yang masih ada:
- pakan posted belum memiliki reversal otomatis yang setara
- transaksi reverse belum memakai wizard pembatalan dengan alasan dan tanggal reversal terpisah

Implikasi:
- alur medis sudah lebih matang secara audit trail dibanding alur pakan

## Area Yang Belum Sepenuhnya Sesuai PSAK 69 Murni
### 5. Pengukuran asset biologis pada fair value less costs to sell
Status: `Gap`

PSAK 69 pada prinsipnya menekankan pengukuran asset biologis pada fair value dikurangi biaya untuk menjual, kecuali dalam kondisi tertentu saat fair value tidak dapat diukur secara andal.

Kondisi modul saat ini:
- nilai dasar sapi dibangun dari biaya historis dan kapitalisasi pra-produksi
- setelah produksi, sapi dibentuk sebagai asset yang disusutkan dengan engine fixed asset
- nilai pasar dan CHKPN dihitung sebagai layer valuasi tambahan, bukan basis pengukuran utama seluruh siklus

Implikasi:
- modul saat ini lebih cocok disebut pendekatan operasional hybrid, bukan implementasi PSAK 69 murni berbasis fair value untuk seluruh asset biologis

### 6. Perubahan fair value periodik langsung ke laba rugi
Status: `Gap`

PSAK 69 biasanya menuntut gain/loss akibat perubahan fair value diakui pada laba rugi periode berjalan.

Kondisi modul saat ini:
- modul menghitung nilai pasar dan CHKPN
- modul menyediakan jurnal impairment/recovery
- modul belum membukukan perubahan fair value periodik sebagai gain/loss fair value movement tersendiri untuk seluruh populasi sapi

Implikasi:
- pendekatan yang sekarang lebih dekat ke monitoring nilai pasar dan impairment, bukan full fair value accounting movement PSAK 69

### 7. Biaya untuk menjual
Status: `Gap`

Kondisi modul saat ini:
- nilai pasar dihitung dari BCS dan harga daging per kg
- belum ada komponen eksplisit `costs to sell`

Implikasi:
- fair value yang digunakan masih fair value kotor, belum `fair value less costs to sell`

## Posisi Modul Saat Ini
Secara praktis, modul saat ini paling tepat diposisikan sebagai:
- sistem traceability asset biologis dan biaya pembesaran sapi perah
- sistem integrasi operasional stok, biaya, dan jurnal sebelum vs sesudah produksi
- sistem kontrol stok lapangan untuk tas petugas medis
- sistem monitoring nilai pasar, CHKPN, dan penyusutan asset produksi
- sistem yang mengadopsi sebagian prinsip PSAK 69, tetapi belum menjadi implementasi PSAK 69 penuh

## Rekomendasi Tahap Berikutnya Bila Ingin Lebih Dekat ke PSAK 69
### Opsi 1. Tambahkan layer fair value movement periodik
Tambahkan proses periodik yang:
- menghitung fair value less costs to sell untuk tiap sapi
- membandingkan dengan carrying amount sebelumnya
- membukukan gain/loss perubahan fair value ke laba rugi

### Opsi 2. Tambahkan master biaya untuk menjual
Tambahkan parameter seperti:
- biaya komisi penjualan
- biaya transport
- biaya pasar atau biaya pelepasan

Lalu ubah formula nilai pasar menjadi:
- `fair value less costs to sell`

### Opsi 3. Bedakan kebijakan akuntansi per fase
Jika perusahaan ingin hybrid policy yang lebih eksplisit, dokumentasikan secara formal:
- fase pembesaran menggunakan pendekatan biaya historis
- fase tertentu menggunakan monitoring fair value
- CHKPN dipakai sebagai kontrol konservatif

### Opsi 4. Tambahkan reversal otomatis untuk pakan
Agar traceability antar proses lebih konsisten, tambahkan:
- reverse journal otomatis
- reverse stock move otomatis
untuk transaksi pakan yang sudah posted

### Opsi 5. Tambahkan kontrol reserved quantity untuk stok tas
Jika kontrol lapangan ingin lebih ketat, validasi saldo tas bisa ditingkatkan agar memperhitungkan reservation dan strategi pengeluaran stok.

## Kesimpulan
Jika pertanyaannya adalah apakah modul sudah mengikuti pola:
- `Traceability`: ya, pada alur utama sudah kuat
- `Inventory Link`: ya untuk pakan dan input medis berbasis stok, termasuk kontrol tas petugas
- `PSAK 69`: belum sepenuhnya, masih ada gap penting di fair value less costs to sell dan gain/loss fair value periodik

Karena itu, klaim yang paling aman saat ini adalah:
- modul sudah mendukung kontrol, jejak transaksi, dan integrasi stok-akuntansi asset biologis yang jauh lebih kuat
- modul sudah mengadopsi sebagian prinsip PSAK 69 dengan kontrol operasional yang lebih baik
- modul belum dapat diklaim sebagai implementasi PSAK 69 penuh tanpa pengembangan tambahan dan validasi kebijakan akuntansi perusahaan

## Versi
Dokumen ini sesuai dengan versi modul:
- `14.0.1.4.0`
