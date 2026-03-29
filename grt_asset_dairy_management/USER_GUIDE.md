# Panduan User

## Tujuan
Panduan ini ditujukan untuk user operasional yang memakai modul `grt_asset_dairy_management` sehari-hari, terutama untuk:
- input data sapi
- update berat badan
- pencatatan bunting dan melahirkan
- pemberian pakan
- distribusi stok medis ke tas petugas
- pencatatan vitamin dan inseminasi
- pengecekan nilai buku, nilai pasar, dan CHKPN

## Menu Utama
Menu yang digunakan user ada di:
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

Setelah disimpan, sistem akan:
- membuat kode asset otomatis
- membuat status awal sapi
- menghitung umur bulan
- menghitung kebutuhan pakan default jika referensinya tersedia

## 2. Update berat badan periodik
Buka form sapi lalu masuk ke tab `Berat Badan Periodik`.

Langkah:
1. Tambahkan baris baru.
2. Isi tanggal timbang.
3. Isi berat badan.
4. Simpan.

Hasil:
- berat terkini sapi ikut berubah
- kebutuhan pakan dihitung ulang

## 3. Set status bunting
Buka form sapi lalu klik tombol `Set Bunting`.

Hasil:
- status siklus sapi menjadi `Bunting`
- riwayat status tersimpan

## 4. Catat melahirkan
Buka form sapi lalu klik tombol `Catat Melahirkan`.

Hasil otomatis:
- status sapi berubah menjadi `Produksi`
- tanggal mulai produksi terisi
- asset sapi produksi dibuat atau disinkronkan
- biaya pra-produksi direklasifikasi ke asset produksi

Jika diperlukan sinkronisasi ulang, gunakan tombol `Sinkron Asset`.

## 5. Posting pemberian pakan
Buka `Dairy Asset Management / Pemberian Pakan` lalu buat transaksi baru.

Langkah:
1. Isi tanggal.
2. Pilih kandang jika ingin menarik sapi dari kandang.
3. Periksa detail sapi.
4. Koreksi qty konsentrat dan rumput bila perlu.
5. Klik `Post`.

Hasil:
- stok pakan keluar otomatis
- jurnal terbentuk otomatis

Aturan akuntansi:
- sapi belum produksi: masuk ke asset biologis belum produksi
- sapi sudah produksi: masuk ke beban pakan produksi

## 6. Distribusi stok medis ke tas petugas
Buka `Dairy Asset Management / Distribusi Stok Medis` lalu buat transaksi baru.

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

## 7. Posting vitamin dan inseminasi
Buka `Dairy Asset Management / Vitamin dan Inseminasi` lalu buat transaksi baru.

Langkah:
1. Isi tanggal.
2. Isi petugas.
3. Pilih `Lokasi Tas Petugas`.
4. Tambahkan sapi.
5. Pilih jenis tindakan: `Vitamin` atau `Inseminasi`.
6. Pilih produk atau jasa.
7. Isi qty dan biaya satuan. Jika produk memakai UoM `ml` atau `cc`, isi sesuai satuan tersebut.
8. Klik `Post`.

Aturan sistem:
- untuk produk stok atau consumable, sistem akan cek stok di tas petugas
- jika stok tas kurang, transaksi akan ditolak
- jika stok cukup, sistem membuat pengeluaran dari tas ke konsumsi medis

Aturan akuntansi:
- sapi belum produksi: menambah nilai buku melalui asset biologis belum produksi
- sapi sudah produksi: masuk ke expense produksi

## 8. Melihat nilai buku, nilai pasar, dan CHKPN
Buka form sapi, lalu lihat tab `Asset Biologis`.

Field penting:
- `Biaya Kapitalisasi Pra-Produksi`
- `Dasar Nilai Buku`
- `Nilai Buku`
- `Nilai Pasar`
- `CHKPN`
- `CHKPN Diakui`

## 9. Revaluasi CHKPN
Buka `Dairy Asset Management / Revaluasi CHKPN`.

Langkah umum:
1. Pilih sapi.
2. Isi atau pastikan harga daging per kg terbaru.
3. Jalankan wizard.

Catatan penting:
- jika memilih `Semua Sapi Aktif`, sistem hanya memproses sapi aktif dengan BCS pada company yang dipilih di wizard
- saat memilih sapi manual, daftar sapi dibatasi ke company wizard dan sapi yang punya BCS
- untuk sapi yang belum punya asset produksi aktif, nilai buku revaluasi memakai `Dasar Nilai Buku`

Hasil:
- sistem membandingkan nilai buku dan nilai pasar
- histori valuasi tersimpan
- jurnal CHKPN terbentuk jika ada selisih yang perlu diakui

## Cara Membaca Status Sapi
Status siklus yang dipakai modul:
- `Belum Produksi`: sapi masih dibesarkan dan biaya akan dikapitalisasi
- `Bunting`: sapi sedang hamil
- `Produksi`: sapi sudah melahirkan dan biaya operasional dibebankan
- `Kering`: sapi masuk masa kering
- `Afkir`: sapi keluar dari siklus normal produksi

## Troubleshooting Ringan
### Transaksi tidak bisa diposting
Cek kemungkinan berikut:
- akun belum disetting
- jurnal belum disetting
- produk belum disetting
- lokasi belum disetting
- qty atau biaya masih nol atau negatif
- untuk produk stok/consumable, pastikan kategori produk tidak memakai automated valuation (`real-time`) pada alur pakan/treatment di modul ini

### Kebutuhan pakan tidak muncul
Periksa:
- tanggal lahir sudah diisi
- berat badan sudah diisi
- referensi pakan untuk umur dan bobot tersebut tersedia

### Nilai asset belum sesuai
Gunakan tombol `Sinkron Asset` pada form sapi setelah memastikan:
- tanggal produksi sudah benar
- transaksi pra-produksi sudah diposting

### CHKPN tidak berubah
Periksa:
- BCS sapi sudah diisi
- harga daging per kg sudah diupdate
- wizard revaluasi sudah dijalankan

### Transaksi treatment ditolak karena stok tas kurang
Periksa:
- distribusi stok medis ke tas petugas sudah diposting
- lokasi tas petugas pada treatment sudah benar
- UoM produk sesuai, misalnya `ml` atau `cc`

## Saran Operasional
- selalu update berat badan sebelum posting pakan jika ada perubahan signifikan
- gunakan tanggal transaksi yang sesuai periode kejadian
- pastikan catat melahirkan dilakukan tepat waktu agar jurnal biaya berpindah dari asset ke expense pada tanggal yang benar
- lakukan distribusi stok medis ke tas sebelum petugas melakukan tindakan di kandang
- lakukan review CHKPN secara periodik, misalnya bulanan
