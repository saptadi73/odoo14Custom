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
- validasi stok tas agar tidak minus

### 7. Saldo dan mutasi stok tas petugas
Modul menyediakan report:
- `Saldo Stok Tas`
- `Mutasi Stok Tas`

Keduanya membaca data stok aktual dan histori `stock.move` yang terjadi pada lokasi tas petugas.

### 8. Reversal otomatis transaksi medis
Jika transaksi medis yang sudah `posted` dibatalkan:
- distribusi stok medis akan membuat `reverse stock move`
- treatment akan membuat `reverse stock move` dan `reverse journal`

Pendekatan ini menjaga traceability tanpa menghapus transaksi yang sudah diposting.

### 9. Asset produksi dan penyusutan
Saat sapi mulai produksi atau dicatat melahirkan:
- sistem membuat asset penyusutan otomatis
- nilai asset dibentuk dari nilai perolehan ditambah kapitalisasi biaya pra-produksi
- sistem membuat jurnal reklasifikasi dari akun asset biologis belum produksi ke akun asset pada kategori asset
- penyusutan periodik dijalankan melalui engine asset Odoo

### 10. Valuasi pasar dan CHKPN
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
- `Dairy Asset Management / Saldo Stok Tas`
- `Dairy Asset Management / Mutasi Stok Tas`
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

## Alur Operasional
### 1. Input sapi baru
Isi minimal identitas sapi, kandang, nilai perolehan, nilai afkir, lama penyusutan, dan berat awal. Sistem akan membuat kode asset, status awal, dan kebutuhan pakan default bila referensi tersedia.

### 2. Update berat badan
Input dari tab `Berat Badan Periodik`. Berat terbaru menjadi dasar kebutuhan pakan.

### 3. Set status bunting
Gunakan tombol `Set Bunting` pada form sapi.

### 4. Catat melahirkan
Gunakan tombol `Catat Melahirkan` atau riwayat melahirkan. Sistem akan mengubah sapi menjadi `Produksi`, membuat asset penyusutan, dan menghitung nilai asset produksi.

### 5. Distribusi stok medis ke tas petugas
Gunakan menu `Distribusi Stok Medis` untuk memindahkan stok dari gudang medis ke tas petugas. Jika lokasi tas belum ada, gunakan tombol `Buat Lokasi Tas`.

### 6. Pemberian vitamin atau inseminasi ke sapi
Gunakan menu `Vitamin dan Inseminasi`. Sistem akan memeriksa stok tas, menolak jika stok kurang, lalu mengeluarkan stok dari tas ke lokasi konsumsi medis dan membuat jurnal sesuai status sapi.

### 7. Monitoring saldo dan mutasi tas
Gunakan menu `Saldo Stok Tas` untuk melihat saldo saat ini per tas dan produk, serta `Mutasi Stok Tas` untuk histori masuk/keluar stok tiap petugas.

### 8. Revaluasi CHKPN
Jalankan wizard `Revaluasi CHKPN` untuk menghitung impairment berdasarkan nilai pasar vs nilai buku.

## Alur Jurnal Akuntansi
### A. Pemberian pakan sebelum melahirkan
- stock move keluar untuk konsentrat dan rumput
- jurnal:
  - debit `Akun Asset Biologis Belum Produksi`
  - credit `Akun Kredit Persediaan Pakan`

### B. Pemberian pakan sesudah melahirkan
- stock move keluar untuk konsentrat dan rumput
- jurnal:
  - debit `Akun Beban Pakan Produksi`
  - credit `Akun Kredit Persediaan Pakan`

### C. Distribusi stok medis ke tas petugas
- stock move dari `Lokasi Gudang Medis` ke `Lokasi Tas Petugas`
- tidak ada jurnal, karena perpindahan ini adalah transfer internal antar lokasi

### D. Vitamin atau inseminasi sebelum melahirkan
- stock move dari `Lokasi Tas Petugas` ke `Lokasi Konsumsi Medis` untuk produk stok
- jurnal:
  - debit `Akun Asset Biologis Belum Produksi`
  - credit `Akun Kredit Vitamin` atau `Akun Kredit Inseminasi`

### E. Vitamin atau inseminasi sesudah melahirkan
- stock move dari `Lokasi Tas Petugas` ke `Lokasi Konsumsi Medis` untuk produk stok
- jurnal:
  - debit `Akun Beban Vitamin Produksi` atau `Akun Beban Inseminasi Produksi`
  - credit `Akun Kredit Vitamin` atau `Akun Kredit Inseminasi`

### F. Reversal distribusi stok medis
- membuat `reverse stock move` dari tas kembali ke gudang medis
- transaksi asli tetap tersimpan sebagai jejak audit

### G. Reversal treatment
- membuat `reverse stock move` dari lokasi konsumsi medis kembali ke tas petugas
- membuat `reverse journal` dengan debit/kredit dibalik
- transaksi asli tetap tersimpan sebagai jejak audit

### H. Reklasifikasi saat mulai produksi
- debit `Akun Asset pada Kategori Asset Sapi Produksi`
- credit `Akun Asset Biologis Belum Produksi`

### I. Penyusutan asset sapi produksi
- debit `Akun Beban Penyusutan`
- credit `Akun Akumulasi Penyusutan`

### J. CHKPN
Jika CHKPN bertambah:
- debit `Akun Beban CHKPN`
- credit `Akun Cadangan CHKPN`

Jika CHKPN menurun atau dipulihkan:
- debit `Akun Cadangan CHKPN`
- credit `Akun Pemulihan CHKPN`

## Rumus Penting
### Kebutuhan pakan
1. Cari referensi pakan berdasarkan umur bulan dan bobot hidup.
2. Jika ditemukan, ambil nilai konsentrat dan rumput dari referensi.
3. Jika tidak ditemukan, gunakan rasio fallback perusahaan.

### Nilai dasar asset produksi
`Nilai Dasar Asset = Nilai Perolehan + Total Kapitalisasi Pra-Produksi`

### Nilai pasar
`Nilai Pasar = Bobot Rata-Rata BCS x Harga Daging per Kg`

### CHKPN
`CHKPN = max(Nilai Buku - Nilai Pasar, 0)`

## Versi
Dokumen ini sesuai dengan versi modul:
- `14.0.1.4.0`
