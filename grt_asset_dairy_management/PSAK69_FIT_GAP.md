# PSAK 69 Fit-Gap

## Tujuan
Dokumen ini memetakan tingkat kesesuaian modul `grt_asset_dairy_management` terhadap prinsip-prinsip utama PSAK 69 Agrikultur. Dokumen ini bukan opini audit atau opini akuntansi formal, tetapi alat bantu implementasi agar tim bisnis, finance, dan developer memahami area yang sudah tertutup dan area yang masih memerlukan kebijakan perusahaan.

## Status Ringkas
Penilaian saat ini:
- `Traceability`: sebagian besar sudah terpenuhi
- `Inventory Link`: sudah terpenuhi untuk pakan dan vitamin berbasis stok
- `PSAK 69 full compliance`: belum sepenuhnya, masih hybrid antara biaya historis, kapitalisasi, fixed asset, dan fair value monitoring

## Prinsip Yang Sudah Cukup Tertutup
### 1. Traceability perubahan nilai
Status: `Fit`

Yang sudah tersedia:
- pakan menghasilkan stock move dan jurnal
- vitamin menghasilkan jurnal, dan bila produk vitamin adalah barang/consumable juga menghasilkan stock move
- inseminasi menghasilkan jurnal
- reklasifikasi saat mulai produksi menghasilkan jurnal tersendiri
- penyusutan asset produksi menghasilkan jurnal periodik dari engine asset
- CHKPN menghasilkan jurnal impairment atau reversal
- histori status, melahirkan, valuasi, dan harga daging tersimpan

Implikasi:
- sebagian besar perubahan nilai yang memengaruhi sapi dapat ditelusuri melalui dokumen operasional dan jurnal akuntansi

### 2. Inventory link untuk input biologis utama
Status: `Partial Fit`

Yang sudah tersedia:
- pakan memotong stok riil melalui `stock.move`
- vitamin memotong stok riil bila produknya berupa barang atau consumable

Gap yang masih ada:
- inseminasi masih diasumsikan sebagai jasa, sehingga tidak memiliki stock move
- reversal stock move untuk pembatalan transaksi posted belum otomatis

Catatan:
- untuk banyak perusahaan, inseminasi memang lebih tepat sebagai jasa dan bukan item inventory, sehingga gap ini tidak selalu menjadi masalah standar

### 3. Pemisahan fase pra-produksi dan pasca-produksi
Status: `Fit`

Yang sudah tersedia:
- sebelum melahirkan, biaya pakan, vitamin, dan inseminasi dikapitalisasi ke asset biologis belum produksi
- sesudah melahirkan, biaya operasional diposting sebagai expense
- saat mulai produksi, biaya pra-produksi direklasifikasi ke asset produksi

Nilai tambah:
- alur ini memberi pemisahan treatment akuntansi yang jelas secara operasional

## Area Yang Belum Sepenuhnya Sesuai PSAK 69 Murni
### 4. Pengukuran asset biologis pada fair value less costs to sell
Status: `Gap`

PSAK 69 pada prinsipnya menekankan pengukuran asset biologis pada fair value dikurangi biaya untuk menjual, kecuali dalam kondisi tertentu saat fair value tidak dapat diukur secara andal.

Kondisi modul saat ini:
- nilai dasar sapi dibangun dari biaya historis dan kapitalisasi pra-produksi
- setelah produksi, sapi dibentuk sebagai asset yang disusutkan dengan engine fixed asset
- nilai pasar dan CHKPN dihitung sebagai layer valuasi tambahan, bukan basis pengukuran utama seluruh siklus

Implikasi:
- modul saat ini lebih cocok disebut pendekatan operasional hybrid, bukan implementasi PSAK 69 murni berbasis fair value untuk seluruh asset biologis

### 5. Perubahan fair value periodik langsung ke laba rugi
Status: `Gap`

PSAK 69 biasanya menuntut gain/loss akibat perubahan fair value diakui pada laba rugi periode berjalan.

Kondisi modul saat ini:
- modul menghitung nilai pasar dan CHKPN
- modul menyediakan jurnal impairment/recovery
- modul belum membukukan perubahan fair value periodik sebagai gain/loss fair value movement tersendiri untuk seluruh populasi sapi

Implikasi:
- pendekatan yang sekarang lebih dekat ke monitoring nilai pasar dan impairment, bukan full fair value accounting movement PSAK 69

### 6. Biaya untuk menjual
Status: `Gap`

Kondisi modul saat ini:
- nilai pasar dihitung dari BCS dan harga daging per kg
- belum ada komponen eksplisit `costs to sell`

Implikasi:
- fair value yang digunakan masih fair value kotor, belum `fair value less costs to sell`

## Posisi Modul Saat Ini
Secara praktis, modul saat ini paling tepat diposisikan sebagai:
- sistem traceability asset biologis dan biaya pembesaran sapi perah
- sistem integrasi operasional dan jurnal sebelum vs sesudah produksi
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

### Opsi 4. Tambahkan reversal otomatis
Agar traceability semakin kuat, tambahkan:
- reverse journal otomatis
- reverse stock move otomatis
untuk transaksi pakan dan vitamin yang sudah posted

## Kesimpulan
Jika pertanyaannya adalah apakah modul sudah mengikuti pola:
- `Traceability`: ya, sebagian besar sudah
- `Inventory Link`: ya untuk pakan, dan sekarang juga untuk vitamin berbasis stok
- `PSAK 69`: belum sepenuhnya, masih ada gap penting di fair value less costs to sell dan gain/loss fair value periodik

Karena itu, klaim yang paling aman saat ini adalah:
- modul sudah mendukung kontrol dan pencatatan asset biologis yang lebih kuat
- modul sudah mengadopsi sebagian prinsip PSAK 69
- modul belum dapat diklaim sebagai implementasi PSAK 69 penuh tanpa pengembangan tambahan dan validasi kebijakan akuntansi perusahaan
