# GRT Asset Dairy Management

## Ringkasan
`grt_asset_dairy_management` adalah modul Odoo 14 untuk pengelolaan asset biologis sapi perah. Modul ini memperluas master sapi dan kandang yang sudah ada, lalu menambahkan pengelolaan nilai buku, kebutuhan pakan, status produksi, riwayat kelahiran, valuasi pasar berbasis BCS, CHKPN, serta jurnal operasional sebelum dan sesudah sapi melahirkan.

Modul ini dirancang untuk memisahkan perlakuan akuntansi antara sapi yang belum produksi dan sapi yang sudah produksi:
- Sebelum melahirkan: biaya terkait sapi dikapitalisasi ke asset biologis belum produksi.
- Sesudah melahirkan: biaya operasional dibebankan ke expense.
- Saat mulai produksi: nilai sapi dibentuk menjadi asset penyusutan dan biaya pra-produksi direklasifikasi ke asset tersebut.

## Dependensi
Modul ini bergantung pada:
- `mail`
- `stock`
- `account`
- `om_account_asset`
- `master_sapi`
- `kandang`

## Fitur Utama
### 1. Master kandang sapi perah
Modul menyesuaikan model kandang yang sudah ada untuk kebutuhan asset dairy management, termasuk identitas kandang dan relasi ke sapi.

### 2. Master sapi sebagai asset biologis
Setiap sapi dapat memiliki informasi berikut:
- kode asset
- tanggal penerimaan
- berat awal dan berat terkini
- umur dalam bulan
- nilai perolehan
- nilai afkir
- lama penyusutan
- tanggal mulai produksi
- status siklus sapi
- referensi pakan
- BCS, nilai pasar, nilai buku, dan CHKPN

### 3. Perhitungan kebutuhan pakan
Kebutuhan pakan dihitung dari referensi umur dan bobot hidup berdasarkan file Excel acuan. Jika tidak ditemukan referensi yang cocok, sistem menggunakan rasio fallback dari konfigurasi perusahaan.

### 4. Riwayat timbang dan status
Modul menyimpan:
- riwayat berat badan periodik
- riwayat status sapi
- riwayat melahirkan

### 5. Pemberian pakan
Transaksi pemberian pakan:
- mengambil stok konsentrat dan rumput melalui `stock.move`
- membuat jurnal otomatis sesuai status sapi
- menghitung default kebutuhan pakan berdasarkan umur dan bobot

### 6. Vitamin dan inseminasi dengan stok dua tahap
Modul menyediakan alur medis dua tahap:
- distribusi stok medis dari gudang ke tas petugas
- konsumsi dari tas petugas ke sapi saat vitamin atau inseminasi dilakukan

Setiap transaksi treatment menghasilkan:
- `stock.move` dari tas ke lokasi konsumsi medis untuk produk stok/consumable
- jurnal otomatis sesuai status sapi

### 7. Asset produksi dan penyusutan
Saat sapi mulai produksi atau dicatat melahirkan:
- sistem membuat asset penyusutan otomatis
- nilai asset dibentuk dari nilai perolehan ditambah kapitalisasi biaya pra-produksi
- sistem membuat jurnal reklasifikasi dari akun asset biologis belum produksi ke akun asset pada kategori asset
- penyusutan periodik dijalankan melalui engine asset Odoo

### 8. Valuasi pasar dan CHKPN
Modul mendukung:
- referensi BCS
- harga daging per kg
- nilai pasar sapi
- nilai buku sapi
- CHKPN
- histori harga daging
- histori valuasi
- wizard revaluasi CHKPN massal

## Struktur Menu
Menu utama modul berada pada:
- `Dairy Asset Management / Sapi Perah`
- `Dairy Asset Management / Kandang`
- `Dairy Asset Management / Pemberian Pakan`
- `Dairy Asset Management / Distribusi Stok Medis`
- `Dairy Asset Management / Vitamin dan Inseminasi`
- `Dairy Asset Management / Referensi Pakan`
- `Dairy Asset Management / Referensi BCS`
- `Dairy Asset Management / Revaluasi CHKPN`
- `Dairy Asset Management / Riwayat Valuasi`
- `Dairy Asset Management / Riwayat Harga Daging`
- `Dairy Asset Management / Pengaturan`

## Konfigurasi Awal
Sebelum modul digunakan, buka menu pengaturan dan isi field berikut.

### Produk dan lokasi
- Produk Konsentrat
- Produk Rumput
- Produk Vitamin
- Produk Inseminasi
- Lokasi Sumber Pakan
- Lokasi Konsumsi Pakan
- Lokasi Gudang Medis
- Lokasi Konsumsi Medis

### Jurnal
- Jurnal Pakan
- Jurnal Kapitalisasi Asset Biologis
- Jurnal Vitamin dan Inseminasi
- Jurnal CHKPN

### Akun
- Akun Kredit Persediaan Pakan
- Akun Asset Biologis Belum Produksi
- Akun Beban Pakan Produksi
- Akun Kredit Vitamin
- Akun Beban Vitamin Produksi
- Akun Kredit Inseminasi
- Akun Beban Inseminasi Produksi
- Akun Beban CHKPN
- Akun Cadangan CHKPN
- Akun Pemulihan CHKPN

### Asset dan analytic
- Kategori Asset Sapi Produksi
- Analytic Account Dairy

### Parameter valuasi
- Harga Daging per Kg
- Rasio Konsentrat fallback
- Rasio Rumput fallback

## Master Referensi Pakan
Referensi pakan disimpan pada model `dairy.feed.reference` dan memuat parameter berikut:
- umur minimum dan maksimum
- berat minimum dan maksimum
- kebutuhan konsentrat per hari
- kebutuhan rumput per hari

Data awal modul sudah diisi dari file Excel acuan. Jika perusahaan memiliki formula tambahan untuk sapi dewasa, data dapat ditambah langsung dari menu `Referensi Pakan`.

## Master Referensi BCS
Referensi BCS disimpan pada model `dairy.bcs.reference` dan memuat:
- nilai BCS
- bobot rata-rata pasar
- referensi harga historis dari sheet acuan

Nilai pasar sapi dihitung dari:
- `bobot rata-rata BCS x harga daging per kg saat ini`

## Alur Operasional
### 1. Input sapi baru
Saat input sapi baru, isi minimal:
- identitas sapi
- tanggal lahir atau tanggal penerimaan
- kandang
- nilai perolehan
- nilai afkir
- lama penyusutan
- berat awal

Sistem akan otomatis menghasilkan:
- kode asset sapi
- status awal
- kebutuhan pakan berdasarkan referensi jika data umur dan bobot tersedia

### 2. Update berat badan
Berat badan periodik dapat diinput dari tab `Berat Badan Periodik`. Berat terbaru akan menjadi dasar:
- kebutuhan pakan
- monitoring kondisi sapi

### 3. Set status bunting
Gunakan tombol `Set Bunting` pada form sapi untuk mengubah status ke bunting dan menyimpan history.

### 4. Catat melahirkan
Gunakan tombol `Catat Melahirkan` atau isi tab riwayat melahirkan. Saat itu sistem akan:
- mengubah lifecycle sapi ke `production`
- menyimpan tanggal mulai produksi
- membuat asset penyusutan otomatis jika belum ada
- menghitung nilai asset berdasarkan nilai perolehan ditambah kapitalisasi biaya pra-produksi
- membuat jurnal reklasifikasi ke asset produksi

### 5. Sinkron asset
Jika ada data lama yang sudah produksi sebelum fitur kapitalisasi aktif, gunakan tombol `Sinkron Asset` pada form sapi untuk memaksa sinkronisasi nilai asset dan jurnal reklasifikasinya.

### 6. Distribusi stok medis ke tas petugas
Gunakan menu `Distribusi Stok Medis` untuk memindahkan stok vitamin atau inseminasi dari gudang medis ke tas petugas.

Langkah ringkas:
1. Isi petugas.
2. Pilih lokasi gudang medis.
3. Pilih lokasi tas petugas.
4. Isi produk dan qty.
5. Post.

Jika lokasi tas belum ada, gunakan tombol `Buat Lokasi Tas` di form distribusi untuk membuat lokasi internal baru secara otomatis.

### 7. Pemberian vitamin atau inseminasi ke sapi
Gunakan menu `Vitamin dan Inseminasi`.

Langkah ringkas:
1. Isi petugas.
2. Pilih lokasi tas petugas.
3. Isi sapi, jenis tindakan, produk, dan qty dalam satuan produk seperti `ml` atau `cc`.
4. Post.

Saat posting, sistem akan:
- memeriksa apakah stok di tas petugas cukup
- menolak posting jika stok tas kurang
- membuat `stock.move` dari tas ke lokasi konsumsi medis untuk produk stok
- membuat jurnal ke asset atau expense sesuai status sapi

## Alur Jurnal Akuntansi
### A. Pemberian pakan sebelum melahirkan
Saat sapi belum produksi, transaksi pakan akan menghasilkan:
- stock move keluar untuk konsentrat dan rumput
- jurnal:
  - debit `Akun Asset Biologis Belum Produksi`
  - credit `Akun Kredit Persediaan Pakan`

Catatan guard akuntansi:
- untuk mencegah double posting, modul menolak posting pakan jika produk konsentrat atau rumput memakai automated valuation (`real-time`)

### B. Pemberian pakan sesudah melahirkan
Saat sapi sudah produksi, transaksi pakan akan menghasilkan:
- stock move keluar untuk konsentrat dan rumput
- jurnal:
  - debit `Akun Beban Pakan Produksi`
  - credit `Akun Kredit Persediaan Pakan`

### C. Distribusi stok medis ke tas petugas
Saat distribusi stok medis dilakukan, sistem membuat:
- stock move dari `Lokasi Gudang Medis` ke `Lokasi Tas Petugas`
- tidak ada jurnal, karena perpindahan ini adalah transfer internal antar lokasi

### D. Vitamin atau inseminasi sebelum melahirkan
Saat sapi belum produksi, transaksi treatment menghasilkan:
- stock move dari `Lokasi Tas Petugas` ke `Lokasi Konsumsi Medis` untuk produk stok
- jurnal:
  - debit `Akun Asset Biologis Belum Produksi`
  - credit `Akun Kredit Vitamin` atau `Akun Kredit Inseminasi`

### E. Vitamin atau inseminasi sesudah melahirkan
Saat sapi sudah produksi, transaksi treatment menghasilkan:
- stock move dari `Lokasi Tas Petugas` ke `Lokasi Konsumsi Medis` untuk produk stok
- jurnal:
  - debit `Akun Beban Vitamin Produksi` atau `Akun Beban Inseminasi Produksi`
  - credit `Akun Kredit Vitamin` atau `Akun Kredit Inseminasi`

Catatan guard akuntansi:
- untuk produk stok/consumable, modul menolak posting treatment jika produk memakai automated valuation (`real-time`) agar tidak terjadi double posting

### F. Reklasifikasi saat mulai produksi
Pada saat sapi mulai produksi, sistem menghitung total biaya pra-produksi yang sudah dikapitalisasi lalu membuat jurnal:
- debit `Akun Asset pada Kategori Asset Sapi Produksi`
- credit `Akun Asset Biologis Belum Produksi`

Nilai yang direklas adalah total kapitalisasi dari pakan, vitamin, dan inseminasi yang telah diposting sebelum tanggal produksi.

### G. Penyusutan asset sapi produksi
Setelah asset produksi terbentuk, penyusutan dilakukan oleh engine `om_account_asset` dengan jurnal:
- debit `Akun Beban Penyusutan`
- credit `Akun Akumulasi Penyusutan`

### H. CHKPN
Saat wizard revaluasi dijalankan, sistem membandingkan nilai buku dan nilai pasar.

Catatan perilaku wizard:
- revaluasi diproses per company sesuai `Company` yang dipilih di wizard
- daftar sapi yang bisa dipilih dibatasi pada sapi aktif yang memiliki BCS dan berada pada company wizard
- jika sapi belum punya asset produksi, nilai buku fallback memakai `Dasar Nilai Buku` (nilai perolehan + kapitalisasi pra-produksi)

Jika CHKPN bertambah:
- debit `Akun Beban CHKPN`
- credit `Akun Cadangan CHKPN`

Jika CHKPN menurun atau dipulihkan:
- debit `Akun Cadangan CHKPN`
- credit `Akun Pemulihan CHKPN`

## Rumus Penting
### Kebutuhan pakan
Urutan logika:
1. Cari referensi pakan berdasarkan umur bulan dan bobot hidup.
2. Jika ditemukan, ambil nilai konsentrat dan rumput dari referensi.
3. Jika tidak ditemukan, gunakan rasio fallback perusahaan.

### Nilai dasar asset produksi
`Nilai Dasar Asset = Nilai Perolehan + Total Kapitalisasi Pra-Produksi`

### Nilai pasar
`Nilai Pasar = Bobot Rata-Rata BCS x Harga Daging per Kg`

### CHKPN
`CHKPN = max(Nilai Buku - Nilai Pasar, 0)`
