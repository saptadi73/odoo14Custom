# Panduan User

## Tujuan
Panduan ini ditujukan untuk user operasional yang memakai modul `grt_asset_dairy_management` sehari-hari, terutama untuk:
- input data sapi
- update berat badan
- pencatatan bunting dan melahirkan
- pemberian pakan
- distribusi stok medis ke tas petugas
- pencatatan vitamin dan inseminasi
- melihat saldo dan mutasi stok tas petugas
- pengecekan nilai buku, nilai pasar, dan CHKPN
- pembatalan transaksi medis yang sudah diposting

## Menu Utama
Menu yang digunakan user ada di:
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

## Sebelum Mulai
Pastikan admin sudah mengisi pengaturan modul, minimal:
- produk pakan, vitamin, dan inseminasi
- lokasi stok pakan
- lokasi gudang medis dan lokasi konsumsi medis
- jurnal dan akun akuntansi
- kategori asset sapi produksi
- harga daging per kg

Jika pengaturan belum lengkap, transaksi tidak bisa diposting.

## Alur Kerja Harian
### 1. Input sapi baru
Buka `Dairy Asset Management / Sapi Perah`, lalu buat data sapi baru.

Field yang disarankan diisi:
- Nama sapi
- Eartag
- Kandang
- Tanggal lahir atau tanggal penerimaan
- Berat badan awal
- Nilai perolehan
- Nilai afkir
- Lama penyusutan
- BCS jika sudah diketahui

### 2. Update berat badan periodik
Buka form sapi lalu masuk ke tab `Berat Badan Periodik`, tambahkan baris baru, isi tanggal timbang dan berat, lalu simpan.

### 3. Set status bunting
Buka form sapi lalu klik tombol `Set Bunting`.

### 4. Catat melahirkan
Buka form sapi lalu klik tombol `Catat Melahirkan`.

Hasil otomatis:
- status sapi berubah menjadi `Produksi`
- tanggal mulai produksi terisi
- asset sapi produksi dibuat atau disinkronkan
- biaya pra-produksi direklasifikasi ke asset produksi

### 5. Posting pemberian pakan
Buka `Dairy Asset Management / Pemberian Pakan`, isi tanggal dan detail sapi, lalu klik `Post`.

Aturan akuntansi:
- sapi belum produksi: masuk ke asset biologis belum produksi
- sapi sudah produksi: masuk ke beban pakan produksi

### 6. Distribusi stok medis ke tas petugas
Buka `Dairy Asset Management / Distribusi Stok Medis`.

Langkah:
1. Isi tanggal.
2. Isi nama petugas.
3. Pilih `Lokasi Gudang Medis`.
4. Pilih `Lokasi Tas Petugas`.
5. Jika lokasi tas belum ada, klik tombol `Buat Lokasi Tas`.
6. Tambahkan produk dan qty.
7. Klik `Post`.

Hasil:
- stok berpindah dari gudang medis ke tas petugas
- tidak ada jurnal karena transfer ini bersifat internal

### 7. Posting vitamin dan inseminasi
Buka `Dairy Asset Management / Vitamin dan Inseminasi`.

Langkah:
1. Isi tanggal.
2. Isi petugas.
3. Pilih `Lokasi Tas Petugas`.
4. Tambahkan sapi.
5. Pilih jenis tindakan: `Vitamin` atau `Inseminasi`.
6. Pilih produk atau jasa.
7. Isi qty dan biaya satuan sesuai UoM produk, misalnya `ml` atau `cc`.
8. Klik `Post`.

Aturan sistem:
- untuk produk stok atau consumable, sistem akan cek stok di tas petugas
- jika stok tas kurang, transaksi akan ditolak
- jika stok cukup, sistem membuat pengeluaran dari tas ke konsumsi medis

Aturan akuntansi:
- sapi belum produksi: menambah nilai buku melalui asset biologis belum produksi
- sapi sudah produksi: masuk ke expense produksi

### 8. Lihat saldo stok tas
Buka `Dairy Asset Management / Saldo Stok Tas` untuk melihat saldo per tas petugas dan per produk.

### 9. Lihat mutasi stok tas
Buka `Dairy Asset Management / Mutasi Stok Tas` untuk melihat histori stok masuk dan keluar pada tas petugas.

### 10. Revaluasi CHKPN
Buka `Dairy Asset Management / Revaluasi CHKPN`.

Catatan penting:
- jika memilih `Semua Sapi Aktif`, sistem hanya memproses sapi aktif dengan BCS pada company yang dipilih di wizard
- saat memilih sapi manual, daftar sapi dibatasi ke company wizard dan sapi yang punya BCS
- untuk sapi yang belum punya asset produksi aktif, nilai buku revaluasi memakai `Dasar Nilai Buku`

### 11. Cancel distribusi stok medis yang sudah posted
Jika distribusi medis sudah `posted` lalu di-cancel:
- sistem akan membuat `reverse stock move`
- stok akan kembali dari tas ke gudang medis
- transaksi asli tetap ada sebagai jejak audit

### 12. Cancel treatment yang sudah posted
Jika treatment sudah `posted` lalu di-cancel:
- sistem akan membuat `reverse stock move`
- sistem akan membuat `reverse journal`
- transaksi asli tetap ada sebagai jejak audit

Anda bisa melihat dokumen reverse pada form transaksi.

## Troubleshooting Ringan
### Transaksi tidak bisa diposting
Cek kemungkinan berikut:
- akun belum disetting
- jurnal belum disetting
- produk belum disetting
- lokasi belum disetting
- qty atau biaya masih nol atau negatif
- untuk produk stok/consumable, pastikan kategori produk tidak memakai automated valuation (`real-time`) pada alur pakan/treatment di modul ini

### Transaksi treatment ditolak karena stok tas kurang
Periksa:
- distribusi stok medis ke tas petugas sudah diposting
- lokasi tas petugas pada treatment sudah benar
- UoM produk sesuai, misalnya `ml` atau `cc`

### CHKPN tidak berubah
Periksa:
- BCS sapi sudah diisi
- harga daging per kg sudah diupdate
- wizard revaluasi sudah dijalankan

## Saran Operasional
- selalu update berat badan sebelum posting pakan jika ada perubahan signifikan
- gunakan tanggal transaksi yang sesuai periode kejadian
- lakukan distribusi stok medis ke tas sebelum petugas melakukan tindakan di kandang
- gunakan menu saldo dan mutasi tas untuk kontrol stok lapangan
- lakukan review CHKPN secara periodik, misalnya bulanan
