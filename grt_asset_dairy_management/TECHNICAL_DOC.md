# Dokumentasi Teknis

## Ringkasan Teknis
`grt_asset_dairy_management` adalah modul Odoo 14 untuk pengelolaan asset biologis sapi perah. Modul ini meng-extend model existing `sapi` dan `kandang.sapi.perah`, lalu menambahkan logika akuntansi, operasional, dan valuasi untuk fase pra-produksi dan pasca-produksi.

Dokumen ini ditujukan untuk developer dan implementor yang perlu memahami struktur model, alur data, logika jurnal, dan titik kustomisasi.

## Struktur Modul
Root modul:
- [__manifest__.py](/c:/addon14/grt_asset_dairy_management/__manifest__.py)
- [README.md](/c:/addon14/grt_asset_dairy_management/README.md)
- [USER_GUIDE.md](/c:/addon14/grt_asset_dairy_management/USER_GUIDE.md)
- [TECHNICAL_DOC.md](/c:/addon14/grt_asset_dairy_management/TECHNICAL_DOC.md)
- [PSAK69_FIT_GAP.md](/c:/addon14/grt_asset_dairy_management/PSAK69_FIT_GAP.md)
- `models/`
- `views/`
- `data/`
- `wizard/`
- `security/`

## Dependensi
- `mail`
- `stock`
- `account`
- `om_account_asset`
- `master_sapi`
- `kandang`

## Model dan Tanggung Jawab
### 1. `sapi` extension
File: [dairy_cow.py](/c:/addon14/grt_asset_dairy_management/models/dairy_cow.py)

Tanggung jawab:
- field tambahan asset biologis
- lifecycle sapi
- integrasi ke asset Odoo
- perhitungan kebutuhan pakan
- perhitungan nilai buku, nilai pasar, dan CHKPN
- riwayat timbang, status, dan melahirkan
- sinkronisasi asset saat mulai produksi

### 2. `dairy.feed.record`
File: [dairy_feeding.py](/c:/addon14/grt_asset_dairy_management/models/dairy_feeding.py)

Tanggung jawab:
- transaksi pemberian pakan
- pengeluaran stok pakan melalui `stock.move`
- jurnal pakan otomatis

### 3. `dairy.medical.stock.transfer`
File: [dairy_medical_stock.py](/c:/addon14/grt_asset_dairy_management/models/dairy_medical_stock.py)

Tanggung jawab:
- distribusi stok medis dari gudang ke tas petugas
- transfer internal stok tanpa jurnal
- reversal otomatis saat transaksi posted di-cancel
- penyiapan stok yang akan dipakai untuk treatment lapangan

Field penting:
- `stock_move_ids`
- `reverse_stock_move_ids`
- `bag_location_id`
- `source_location_id`

Method penting:
- `action_open_bag_location_wizard`
- `action_post`
- `_create_reverse_stock_moves`
- `action_cancel`

### 4. `dairy.treatment.record`
File: [dairy_treatment.py](/c:/addon14/grt_asset_dairy_management/models/dairy_treatment.py)

Tanggung jawab:
- transaksi vitamin dan inseminasi
- konsumsi stok dari tas petugas ke konsumsi medis
- validasi stok tas petugas agar tidak minus
- jurnal otomatis pra-produksi vs pasca-produksi
- reversal otomatis stock move dan journal move saat cancel

Field penting:
- `journal_move_id`
- `reverse_journal_move_id`
- `stock_move_ids`
- `reverse_stock_move_ids`
- `bag_location_id`
- `person_in_charge`

Method penting:
- `action_open_bag_location_wizard`
- `_get_medical_consumption_location`
- `_get_available_bag_qty`
- `_validate_line_before_post`
- `_create_stock_moves`
- `_create_reverse_stock_moves`
- `_create_reverse_journal_move`
- `action_cancel`

### 5. Report saldo dan mutasi tas
File: [dairy_medical_stock.py](/c:/addon14/grt_asset_dairy_management/models/dairy_medical_stock.py)

Model report:
- `dairy.bag.stock.report`
- `dairy.bag.movement.report`

Tanggung jawab:
- menampilkan saldo stok aktual pada lokasi tas petugas
- menampilkan mutasi masuk/keluar stok tas berdasarkan `stock.move`
- membangun SQL view secara aman walau salah satu tabel sumber belum ada saat init registry

Helper penting:
- `dairy.bag.report.mixin._existing_bag_location_sources`

### 6. Wizard lokasi tas petugas
File: [dairy_bag_location_wizard.py](/c:/addon14/grt_asset_dairy_management/wizard/dairy_bag_location_wizard.py)

Tanggung jawab:
- membuat lokasi internal `Tas - <Petugas>`
- menghubungkan lokasi itu langsung ke transaksi distribusi atau treatment yang sedang aktif

### 7. `res.company` extension
File: [dairy_config.py](/c:/addon14/grt_asset_dairy_management/models/dairy_config.py)

Tanggung jawab:
- seluruh konfigurasi produk, lokasi, akun, jurnal, ratio fallback, dan valuasi pasar

Konfigurasi penting tambahan untuk alur medis dua tahap:
- `dairy_medical_source_location_id`
- `dairy_medical_consumption_location_id`

### 8. Wizard revaluasi CHKPN
File: [dairy_revaluation_wizard.py](/c:/addon14/grt_asset_dairy_management/wizard/dairy_revaluation_wizard.py)

Tanggung jawab:
- revaluasi CHKPN per company
- pembatasan sapi aktif yang punya BCS dan sesuai company wizard
- pencatatan histori valuasi dan histori harga daging
- pembuatan jurnal impairment atau recovery bila opsi jurnal diaktifkan

## Alur Data Utama
### A. Distribusi stok medis ke tas petugas
1. User membuat `dairy.medical.stock.transfer`.
2. User pilih gudang medis dan lokasi tas petugas.
3. `action_post()` membuat `stock.move` dari gudang ke tas.
4. Tidak ada jurnal karena hanya transfer internal antar lokasi.

### B. Konsumsi vitamin atau inseminasi
1. User membuat `dairy.treatment.record`.
2. User pilih tas petugas.
3. Sistem validasi stok tas per produk dengan `stock.quant`.
4. Jika stok tas kurang, posting ditolak.
5. Jika stok cukup dan produk bertipe stok/consumable, sistem membuat `stock.move` dari tas ke lokasi konsumsi medis.
6. Sistem membuat jurnal treatment sesuai status sapi.

### C. Reversal distribusi medis
1. User cancel transaksi distribusi yang sudah posted.
2. Sistem membuat `reverse stock move` dari tas kembali ke gudang.
3. Transaksi diubah ke status `cancel`, tetapi move awal dan reverse tetap tersimpan.

### D. Reversal treatment
1. User cancel transaksi treatment yang sudah posted.
2. Sistem membuat `reverse stock move` dari konsumsi medis kembali ke tas untuk produk stok.
3. Sistem membuat `reverse journal move` dengan debit/kredit dibalik.
4. Semua dokumen reverse disimpan pada transaksi yang sama.

### E. Report saldo dan mutasi tas
- `Saldo Stok Tas` membaca saldo quant pada lokasi tas
- `Mutasi Stok Tas` membaca pergerakan `stock.move` masuk dan keluar dari lokasi tas

## Logika Jurnal Medis
### Transfer gudang ke tas
- stock move internal
- tanpa jurnal

### Treatment sebelum produksi
- debit `Akun Asset Biologis Belum Produksi`
- credit `Akun Kredit Vitamin` atau `Akun Kredit Inseminasi`

### Treatment sesudah produksi
- debit `Akun Beban Vitamin Produksi` atau `Akun Beban Inseminasi Produksi`
- credit `Akun Kredit Vitamin` atau `Akun Kredit Inseminasi`

### Reverse treatment
- stock move dibalik untuk item stok
- journal move dibalik 1:1 dari move asli
- transaksi lama tidak dihapus agar audit trail tetap utuh

## View dan Menu Tambahan
### View utama
- [dairy_medical_stock_views.xml](/c:/addon14/grt_asset_dairy_management/views/dairy_medical_stock_views.xml)
- [dairy_treatment_views.xml](/c:/addon14/grt_asset_dairy_management/views/dairy_treatment_views.xml)
- [dairy_bag_location_wizard_views.xml](/c:/addon14/grt_asset_dairy_management/wizard/dairy_bag_location_wizard_views.xml)

### Menu tambahan
- `Dairy Asset Management / Distribusi Stok Medis`
- `Dairy Asset Management / Saldo Stok Tas`
- `Dairy Asset Management / Mutasi Stok Tas`

### Tombol tambahan
- `Buat Lokasi Tas` pada form distribusi stok medis
- `Buat Lokasi Tas` pada form treatment
- `Cancel` pada distribusi medis posted untuk membuat reverse stock move
- `Cancel` pada treatment posted untuk membuat reverse stock move dan reverse journal

## Titik Kustomisasi yang Umum
### 1. Struktur lokasi tas petugas
Jika perusahaan ingin tas petugas dibuat di parent location tertentu, sesuaikan default wizard pada:
- `dairy.bag.location.wizard.default_get`

### 2. Validasi stok tas
Jika ingin memperhitungkan reservation atau aturan FEFO, sesuaikan:
- `dairy.treatment.record.line._get_available_bag_qty`

### 3. Transfer medis berjurnal
Jika perusahaan ingin transfer gudang ke tas ikut dijurnal, tambahkan journal entry pada:
- `dairy.medical.stock.transfer.action_post`

### 4. Reversal journal dengan metadata tambahan
Jika reverse journal perlu analytic tags, partner rules, atau narasi khusus, sesuaikan:
- `dairy.treatment.record._create_reverse_journal_move`

## Known Limitations
- transfer gudang ke tas belum dijurnal karena dianggap perpindahan internal
- validasi stok tas menggunakan total quant, belum mempertimbangkan reserved quantity secara spesifik
- modul menggunakan jurnal manual untuk pakan/treatment; karena itu posting ditolak untuk produk dengan automated valuation (`real-time`) guna mencegah double posting

## Versi
Dokumen ini sesuai dengan versi modul:
- `14.0.1.4.0`
