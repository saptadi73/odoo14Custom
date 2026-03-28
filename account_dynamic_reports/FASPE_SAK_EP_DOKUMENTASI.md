# Dokumentasi Laporan Keuangan FASPE / SAK EP
## Modul: `account_dynamic_reports` — Versi 14.2.0

---

## Daftar Isi

1. [Latar Belakang](#1-latar-belakang)
2. [Ruang Lingkup Implementasi](#2-ruang-lingkup-implementasi)
3. [Arsitektur Teknis](#3-arsitektur-teknis)
4. [Model Data](#4-model-data)
5. [Logika Bisnis & Alur Kalkulasi](#5-logika-bisnis--alur-kalkulasi)
6. [Validasi dan Aturan Bisnis](#6-validasi-dan-aturan-bisnis)
7. [Panduan Penggunaan (User Guide)](#7-panduan-penggunaan-user-guide)
8. [Konfigurasi Prasyarat](#8-konfigurasi-prasyarat)
9. [Hak Akses (Security)](#9-hak-akses-security)
10. [Referensi File Kode](#10-referensi-file-kode)
11. [Troubleshooting](#11-troubleshooting)
12. [Changelog](#12-changelog)

---

## 1. Latar Belakang

### 1.1 Apa itu FASPE / SAK EP?

**FASPE** *(Financial Accounting Standards for Private Entities)* adalah versi bahasa Inggris dari **SAK EP** *(Standar Akuntansi Keuangan Entitas Privat)* — standar pelaporan keuangan yang diterbitkan oleh Ikatan Akuntan Indonesia (IAI) khusus untuk entitas privat (bukan entitas publik/Tbk).

SAK EP merupakan penyederhanaan dari SAK berbasis IFRS full, dirancang agar entitas non-publik dapat menyusun laporan keuangan yang informatif namun tidak terlalu kompleks. Standar ini menggantikan SAK ETAP (Entitas Tanpa Akuntabilitas Publik) secara bertahap.

### 1.2 Relevansi dalam Konteks Multi-Company

Dalam grup usaha yang terdiri dari beberapa entitas hukum (misalnya induk dan anak perusahaan), laporan keuangan konsolidasi diperlukan untuk memberikan gambaran posisi keuangan grup secara keseluruhan. Proses konsolidasi memerlukan:

- **Agregasi saldo** dari seluruh company dalam grup
- **Eliminasi transaksi intra-grup** (piutang/utang antar company, investasi, dll.) agar tidak terjadi penghitungan ganda
- **Penyajian bersih** atas posisi Aset, Liabilitas, dan Ekuitas setelah eliminasi

### 1.3 Fitur yang Dibangun

Implementasi ini menambahkan menu **Laporan Keuangan FASPE** yang berdiri sendiri di dalam modul `account_dynamic_reports` Odoo 14, terpisah dari laporan keuangan yang sudah ada (General Ledger, Trial Balance, dll.).

Fitur utama:
- Pilih rentang periode bebas
- Pilih 2 atau lebih company yang akan dikonsolidasi
- Tentukan akun eliminasi per company secara spesifik
- Tampilkan laporan neraca konsolidasi dengan kolom: Sebelum Eliminasi, Eliminasi, Setelah Eliminasi
- Validasi otomatis (minimal 2 company, kesamaan mata uang, konsistensi tanggal)
- Baris *check* otomatis: Aset − (Liabilitas + Ekuitas) harus = 0

---

## 2. Ruang Lingkup Implementasi

### 2.1 Yang Termasuk dalam Scope

| Komponen | Keterangan |
|---|---|
| Laporan Neraca Konsolidasi | Aset, Liabilitas, Ekuitas per akun, dikonsolidasikan dari semua company terpilih |
| Eliminasi Intra-Grup | Per company, per akun. Saldo akun yang dieliminasi dikurangkan dari total konsolidasi |
| Validasi input | Minimal 2 company, tanggal konsisten, mata uang sama |
| Hasil read-only | Halaman laporan tidak bisa diedit/dihapus → hanya dibaca |
| Balance check | Baris check otomatis menampilkan selisih Aset − (Liabilitas + Ekuitas) |

### 2.2 Yang Tidak Termasuk dalam Scope (di luar versi ini)

| Komponen | Keterangan |
|---|---|
| Laporan Laba Rugi Konsolidasi | Belum ada; hanya neraca (Balance Sheet) |
| Ekspor PDF / XLSX | Belum diimplementasikan untuk FASPE |
| Laporan Arus Kas Konsolidasi | Belum ada |
| Jurnal eliminasi otomatis | Hanya kalkulasi di laporan saja, tidak membuat journal entries |
| Multi-currency conversion | Tidak ada; semua company harus pakai mata uang sama |

---

## 3. Arsitektur Teknis

### 3.1 Pola 3-Layer Report

Mengikuti pola yang sama dengan semua report eksisting di modul `account_dynamic_reports`:

```
[Menu Item]
    ↓  trigger action
[ir.actions.act_window] (target="new")
    ↓  buka popup wizard
[Wizard Form — ins.faspe.consolidated.wizard]
    ↓  klik "Tampilkan Laporan"
    ↓  action_generate_report() → create ins.faspe.consolidated.report
[Report Form — ins.faspe.consolidated.report] (target="current", read-only)
```

### 3.2 Diagram Alur Eksekusi

```
User klik "Laporan Keuangan FASPE"
        │
        ▼
[Popup Wizard Form]
  - Pilih date_from, date_to
  - Pilih company_ids (min. 2)
  - Isi elimination_line_ids (opsional)
  - Klik "Tampilkan Laporan"
        │
        ▼
[action_generate_report()]
  1. _validate_input()          → cek rules bisnis
  2. _prepare_account_payload() → read_group dari account.move.line
  3. _prepare_elimination_payload() → hitung eliminasi per akun
  4. _prepare_report_lines()    → bangun list baris laporan
  5. create ins.faspe.consolidated.report + line_ids
  6. return act_window → buka halaman report
        │
        ▼
[Halaman Report — Read Only]
  - Header: judul, periode, company, currency
  - Ringkasan: total per section + selisih check
  - Tabel detail: per akun, 3 kolom nominal
```

### 3.3 Stack Teknis

| Item | Nilai |
|---|---|
| Platform | Odoo 14.0-20231205 |
| Python | 3.7.7 (`C:/odoo14c/python/python.exe`) |
| Database | PostgreSQL, db: `kanjabung_MRP` |
| Server | `C:/odoo14c/server/odoo-bin` |
| Config | `C:/addon14/odoo.conf` |
| Modul | `account_dynamic_reports` |
| Model storage | `TransientModel` (tabel sementara, auto-vacuum) |

---

## 4. Model Data

### 4.1 `ins.faspe.consolidated.wizard`

Wizard input pengguna. Bersifat sementara (`TransientModel`).

| Field | Tipe | Wajib | Keterangan |
|---|---|---|---|
| `title` | `Char` | — | Judul laporan, auto-fill, readonly |
| `date_from` | `Date` | Ya | Tanggal awal periode; default 1 Jan tahun berjalan |
| `date_to` | `Date` | Ya | Tanggal akhir periode; default hari ini |
| `target_move` | `Selection` | Ya | `posted` = hanya entri terposting; `all` = semua |
| `company_ids` | `Many2many` → `res.company` | Ya | Company yang dikonsolidasikan (min. 2) |
| `company_id` | `Many2one` → `res.company` | Ya | Company utama (hidden, dipakai sebagai referensi currency) |
| `currency_id` | `Many2one` → `res.currency` | — | Terambil otomatis dari `company_id`, readonly |
| `elimination_line_ids` | `One2many` → `ins.faspe.consolidated.elimination.line` | — | Daftar akun eliminasi per company |

**Methods penting:**
- `_onchange_company_ids()` — sinkronisasi baris eliminasi ketika pilihan company berubah
- `_validate_input()` — pengecekan rules bisnis sebelum laporan digenerate
- `_get_move_line_domain()` — membangun domain filter untuk query ke `account.move.line`
- `_prepare_account_payload()` — eksekusi `read_group` dan aggregasi saldo per akun
- `_prepare_elimination_payload()` — menghitung total eliminasi per akun berdasarkan `elimination_line_ids`
- `_prepare_report_lines()` — merakit list baris laporan dengan urutan section/akun/total/check
- `action_generate_report()` — entry point tombol "Tampilkan Laporan"

---

### 4.2 `ins.faspe.consolidated.elimination.line`

Baris eliminasi intra-grup, bersifat sementara.

| Field | Tipe | Wajib | Keterangan |
|---|---|---|---|
| `wizard_id` | `Many2one` → `ins.faspe.consolidated.wizard` | Ya | Parent wizard; cascade delete |
| `company_id` | `Many2one` → `res.company` | Ya | Company pemilik akun yang dieliminasi |
| `account_ids` | `Many2many` → `account.account` | — | Akun yang saldo-nya akan dieliminasi dari konsolidasi |

**Catatan domain:** `account_ids` dibatasi hanya akun milik `company_id` dengan `internal_group` = `asset`, `liability`, atau `equity`.

---

### 4.3 `ins.faspe.consolidated.report`

Header laporan hasil. Dibuat otomatis oleh `action_generate_report()`.

| Field | Tipe | Keterangan |
|---|---|---|
| `title` | `Char` | Judul dari wizard |
| `generated_at` | `Datetime` | Timestamp pembuatan laporan |
| `date_from` / `date_to` | `Date` | Rentang periode |
| `target_move` | `Selection` | Filter entri |
| `company_ids` | `Many2many` → `res.company` | Daftar company yang dikonsolidasikan |
| `company_names` | `Char` | Nama company dirangkai dengan koma (untuk display) |
| `currency_id` | `Many2one` → `res.currency` | Mata uang laporan |
| `elimination_total` | `Monetary` | Total nominal akun yang dieliminasi |
| `total_assets` | `Monetary` | Total saldo Aset setelah eliminasi |
| `total_liabilities` | `Monetary` | Total saldo Liabilitas setelah eliminasi |
| `total_equity` | `Monetary` | Total saldo Ekuitas setelah eliminasi |
| `balance_difference` | `Monetary` | Aset − (Liabilitas + Ekuitas); idealnya = 0 |
| `line_ids` | `One2many` → `ins.faspe.consolidated.report.line` | Baris detail |

---

### 4.4 `ins.faspe.consolidated.report.line`

Baris detail laporan, terurut berdasarkan `sequence, id`.

| Field | Tipe | Keterangan |
|---|---|---|
| `report_id` | `Many2one` | Parent report; cascade delete |
| `sequence` | `Integer` | Urutan tampil (kelipatan 10) |
| `line_type` | `Selection` | `section` / `account` / `total` / `check` |
| `section` | `Selection` | `asset` / `liability` / `equity` / `check` |
| `account_code` | `Char` | Kode akun (kosong untuk section/total/check) |
| `name` | `Char` | Nama akun atau judul section |
| `amount_before_elimination` | `Monetary` | Saldo agregat sebelum eliminasi |
| `elimination_amount` | `Monetary` | Besaran yang dieliminasi |
| `amount` | `Monetary` | Saldo bersih setelah eliminasi |

**Aturan tampil (dekorasi XML):**
- `line_type = 'section'` atau `'total'` → **bold** (`decoration-bf`)
- `line_type = 'check'` → warna biru info (`decoration-info`)

---

## 5. Logika Bisnis & Alur Kalkulasi

### 5.1 Pengambilan Data Saldo (`_prepare_account_payload`)

Query ke `account.move.line` menggunakan `read_group` dengan parameter:

```python
aml_obj.read_group(
    domain=[
        ('company_id', 'in', self.company_ids.ids),
        ('account_id.internal_group', 'in', ['asset', 'liability', 'equity']),
        ('date', '>=', self.date_from),
        ('date', '<=', self.date_to),
        # + ('move_id.state', '=', 'posted') jika target_move = 'posted'
    ],
    fields=['balance', 'account_id', 'company_id'],
    groupby=['account_id', 'company_id'],
    lazy=False,
)
```

Hasil dikelompokkan menjadi dua struktur:
1. **`payload`** — saldo agregat per akun (lintas semua company): `{account_id: {code, name, internal_group, balance}}`
2. **`balance_by_company_account`** — saldo per pasangan (company, akun): `{(company_id, account_id): balance}` — dipakai untuk menghitung eliminasi yang tepat.

### 5.2 Kalkulasi Eliminasi (`_prepare_elimination_payload`)

```
Untuk setiap elimination_line:
    Untuk setiap account dalam elimination_line.account_ids:
        elimination_by_account[account_id] += balance_by_company_account[(company_id, account_id)]
        elimination_total += jumlah tersebut
```

Eliminasi bersifat **additive per akun** — jika akun yang sama muncul di dua elimination_line berbeda (company berbeda), kedua nilainya dijumlahkan.

### 5.3 Perakitan Baris Laporan (`_prepare_report_lines`)

Urutan section: **ASET → LIABILITAS → EKUITAS**

Untuk setiap section:
1. Baris header section (type = `section`, bold)
2. Baris per akun, diurutkan berdasarkan `account_code` lalu `name` (type = `account`)
3. Baris total section (type = `total`, bold)

Setelah semua section:
4. Baris check (type = `check`, warna biru):
   `CHECK ASET - (LIABILITAS + EKUITAS)` = `total_assets - (total_liabilities + total_equity)`

**Catatan:** Akun dengan saldo nol (setelah eliminasi) **dan** eliminasi nol akan di-skip (`continue`) — tidak dimunculkan di laporan agar tetap ringkas.

### 5.4 Rumus Keseimbangan Neraca

$$\text{balance\_difference} = \text{Total Aset} - (\text{Total Liabilitas} + \text{Total Ekuitas})$$

Nilai ini idealnya = **0**. Jika tidak nol, dapat mengindikasikan:
- Ada akun yang `internal_group`-nya salah di Chart of Accounts
- Ada eliminasi yang tidak seimbang (mengeliminasi satu sisi tanpa sisi lawan)
- Ada jurnal yang belum di-posting (jika filter = `posted`)

---

## 6. Validasi dan Aturan Bisnis

Semua validasi dijalankan di method `_validate_input()` sebelum query ke database.

| # | Kondisi yang Dicek | Pesan Error |
|---|---|---|
| 1 | `len(company_ids) < 2` | "Pilih minimal 2 company untuk laporan consolidated multi company." |
| 2 | `date_from` atau `date_to` kosong | "Tanggal Mulai dan Tanggal Akhir wajib diisi." |
| 3 | `date_from > date_to` | "Tanggal Mulai tidak boleh lebih besar dari Tanggal Akhir." |
| 4 | Company-company memiliki mata uang berbeda | "Semua company yang dikonsolidasikan harus menggunakan mata uang yang sama agar presisi laporan terjaga." |

Selain itu, setelah query jika tidak ada data:

| # | Kondisi | Pesan Error |
|---|---|---|
| 5 | `payload` kosong (tidak ada move line) | "Tidak ada data akun neraca pada rentang tanggal dan filter yang dipilih." |

---

## 7. Panduan Penggunaan (User Guide)

### 7.1 Mengakses Menu

1. Login ke Odoo sebagai user dengan role **Accounting / Accountant** atau **Accounting / Adviser**
2. Buka modul **Accounting**
3. Di menu laporan (biasanya **Accounting → Reports** atau sesuai konfigurasi menu `account_reports_ins`), pilih **"Laporan Keuangan FASPE"**

### 7.2 Mengisi Wizard Input

Popup wizard akan muncul dengan bagian:

**Bagian Periode:**
| Field | Cara Isi |
|---|---|
| Tanggal Mulai | Pilih tanggal awal periode laporan |
| Tanggal Akhir | Pilih tanggal akhir periode laporan |
| Target Moves | Pilih `All Posted Entries` untuk hanya memuat jurnal yang sudah di-posting, atau `All Entries` untuk semua |

**Bagian Konsolidasi Multi Company:**
| Field | Cara Isi |
|---|---|
| Companies | Pilih 2 atau lebih company yang akan dikonsolidasikan. Field ini hanya tampil jika user aktif di lingkungan multi-company (`base.group_multi_company`). |
| Currency | Terisi otomatis dari company utama; pastikan semua company terpilih menggunakan mata uang yang sama. |

**Bagian Akun Eliminasi per Company:**

Setelah memilih company, tabel eliminasi akan terisi otomatis dengan satu baris per company. Isi kolom **Akun yang Di-eliminasi** untuk setiap company:
- Klik pada kolom akun di baris company yang ingin diatur
- Pilih satu atau lebih akun yang saldo-nya harus dieliminasi (misalnya: akun piutang antar company, akun investasi pada anak perusahaan)
- Daftar akun dibatasi hanya akun kepunyaan company tersebut dengan `internal_group` = Aset/Liabilitas/Ekuitas

> **Catatan:** Bagian eliminasi bersifat opsional. Jika tidak diisi, laporan akan menampilkan konsolidasi tanpa eliminasi.

### 7.3 Membaca Halaman Laporan

Setelah klik **"Tampilkan Laporan"**, halaman laporan akan terbuka dengan:

**Header:**
- Judul laporan
- Tanggal dibuat (`generated_at`)
- Filter target entries
- Periode laporan
- Daftar company yang dikonsolidasikan

**Ringkasan Konsolidasi:**
| Field | Arti |
|---|---|
| Total Eliminasi | Jumlah nominal seluruh akun yang dieliminasi |
| Total Aset | Saldo aset konsolidasi bersih setelah eliminasi |
| Total Liabilitas | Saldo liabilitas konsolidasi bersih setelah eliminasi |
| Total Ekuitas | Saldo ekuitas konsolidasi bersih setelah eliminasi |
| Selisih Aset − (Liabilitas + Ekuitas) | Idealnya = 0; jika tidak nol, perlu investigasi |

**Tabel Detail Laporan:**

Tabel berisi kolom:
- **Kode Akun** — kode akun Chart of Accounts
- **Nama** — nama akun atau judul section/total
- **Sebelum Eliminasi** — saldo agregat dari semua company sebelum eliminasi diterapkan
- **Eliminasi** — nominal yang dieliminasi untuk akun tersebut
- **Setelah Eliminasi** — saldo bersih: Sebelum Eliminasi − Eliminasi

Penyajian tabel:
- Baris **section** (ASET, LIABILITAS, EKUITAS) dan baris **total** ditampilkan **tebal** (bold)
- Baris **check** ditampilkan dengan warna **biru**
- Baris akun ditampilkan normal, diurutkan berdasarkan kode akun

### 7.4 Menutup dan Membuat Laporan Baru

- Laporan bersifat **TransientModel** — data otomatis terhapus setelah sesi berakhir atau setelah vacuum oleh Odoo
- Untuk membuat laporan baru dengan periode/company berbeda, kembali ke menu dan buka wizard kembali
- Halaman laporan bersifat **read-only** — tidak bisa diedit atau dihapus secara manual

---

## 8. Konfigurasi Prasyarat

### 8.1 Multi-Company Odoo

Fitur ini membutuhkan setup multi-company di Odoo:
1. Masuk ke **Settings → Companies** — tambahkan minimal 2 company
2. Pastikan user memiliki akses ke semua company yang akan dikonsolidasikan (**Settings → Users → [user] → Companies**)
3. Aktifkan fitur multi-company: **Settings → General Settings → Companies → Allow multi-company**

### 8.2 Chart of Accounts

Setiap company harus memiliki **Chart of Accounts** yang sudah dikonfigurasi dengan benar, khususnya:
- Field `internal_group` pada setiap akun harus diset: `asset`, `liability`, atau `equity` (bukan `income`, `expense`, atau `off_balance`)
- Tanpa konfigurasi ini, saldo akun tersebut tidak akan muncul di laporan FASPE

### 8.3 Mata Uang

- Semua company yang akan dikonsolidasikan **harus menggunakan mata uang yang sama**
- Konfigurasi di: **Settings → Companies → [company] → Currency**
- Konsolidasi multi-currency belum didukung di versi ini

### 8.4 Journal Entries

- Pastikan semua jurnal relevan sudah dalam status **Posted** jika menggunakan filter `All Posted Entries`
- Gunakan filter `All Entries` untuk memasukkan draft entries dalam laporan (berguna untuk preview)

---

## 9. Hak Akses (Security)

Empat model baru terdaftar di `security/ir.model.access.csv` dengan akses penuh bagi group `account.group_account_user` (Accounting User):

| Access ID | Model | Group | Read | Write | Create | Delete |
|---|---|---|---|---|---|---|
| `access_ins_faspe_consolidated_wizard` | `ins.faspe.consolidated.wizard` | `account.group_account_user` | 1 | 1 | 1 | 1 |
| `access_ins_faspe_consolidated_elimination_line` | `ins.faspe.consolidated.elimination.line` | `account.group_account_user` | 1 | 1 | 1 | 1 |
| `access_ins_faspe_consolidated_report` | `ins.faspe.consolidated.report` | `account.group_account_user` | 1 | 1 | 1 | 1 |
| `access_ins_faspe_consolidated_report_line` | `ins.faspe.consolidated.report.line` | `account.group_account_user` | 1 | 1 | 1 | 1 |

Menu item `account_report_faspe_consolidated` juga dikunci dengan `groups="account.group_account_user"`, sehingga hanya akuntan yang bisa mengaksesnya.

---

## 10. Referensi File Kode

| File | Peran |
|---|---|
| `wizard/faspe_consolidated_report.py` | Core logic: 4 model TransientModel, semua method kalkulasi |
| `wizard/faspe_consolidated_report_view.xml` | Definisi view wizard input, form laporan, action, menuitem |
| `wizard/__init__.py` | Import `faspe_consolidated_report` |
| `__manifest__.py` | Versi `14.2.0`; `faspe_consolidated_report_view.xml` di list `data` |
| `security/ir.model.access.csv` | 4 baris akses untuk model baru |

### 10.1 Ringkasan Perubahan dari Versi 14.1.0 ke 14.2.0

```
+ wizard/faspe_consolidated_report.py       (BARU)
+ wizard/faspe_consolidated_report_view.xml (BARU)
~ wizard/__init__.py                        (tambah import)
~ __manifest__.py                           (versi + data entry baru)
~ security/ir.model.access.csv             (4 baris baru)
```

---

## 11. Troubleshooting

### 11.1 "Pilih minimal 2 company..."

**Penyebab:** User hanya memilih 1 company (atau tidak ada) di field `Companies`.

**Solusi:** Pastikan minimal 2 company dipilih. Jika field `Companies` tidak tampil, user mungkin tidak diaktifkan dalam mode multi-company — aktifkan terlebih dahulu di **Settings → Users → [user] → Companies**.

---

### 11.2 "Semua company yang dikonsolidasikan harus menggunakan mata uang yang sama..."

**Penyebab:** Company-company yang dipilih memiliki pengaturan `Currency` berbeda.

**Solusi:** Samakan mata uang di **Settings → Companies → [tiap company] → Currency**. Jika membutuhkan multi-currency, fitur ini belum tersedia di versi ini.

---

### 11.3 "Tidak ada data akun neraca pada rentang tanggal..."

**Penyebab:** Tidak ada `account.move.line` yang memenuhi semua kondisi filter:
- Company dalam `company_ids`
- `account_id.internal_group` = asset/liability/equity
- `date` dalam rentang `date_from` – `date_to`
- (opsional) `move_id.state = posted`

**Solusi:**
1. Perluas rentang tanggal
2. Coba ganti filter ke `All Entries`
3. Pastikan Chart of Accounts sudah ada dan transaksi sudah diinput

---

### 11.4 `balance_difference` Tidak Nol

**Penyebab umum:**
- Ada akun dengan `internal_group` yang tidak tepat (misalnya akun modal di-set sebagai `asset`)
- Eliminasi tidak seimbang (mengeliminasi satu sisi tanpa pasangannya — misalnya hanya mengeliminasi piutang antar-company tanpa mengeliminasi utang antar-company yang sesuai)
- Ada transaksi yang belum di-posting (gunakan `All Entries` untuk cek)

**Langkah investigasi:**
1. Lihat kolom **Sebelum Eliminasi** — sudah seimbang sebelum eliminasi? Jika tidak, periksa `internal_group` akun
2. Lihat kolom **Eliminasi** — apakah eliminasi dilakukan di kedua sisi? Misalnya eliminasi piutang company A sekaligus eliminasi utang company B

---

### 11.5 Menu "Laporan Keuangan FASPE" Tidak Muncul

**Kemungkinan penyebab:**
1. Modul belum di-upgrade setelah update kode
2. User tidak memiliki group `account.group_account_user`
3. Cache browser

**Solusi:**
```powershell
# Upgrade modul
C:/odoo14c/python/python.exe C:/odoo14c/server/odoo-bin `
  --config=C:/addon14/odoo.conf `
  --database=kanjabung_MRP `
  --without-demo=all `
  -u account_dynamic_reports `
  --stop-after-init
```
Kemudian refresh browser (Ctrl+F5).

---

### 11.6 Error Saat Upgrade — `ParseError` pada XML

**Catatan historis:** Error ini sudah diperbaiki. Odoo 14 menolak tag `<label string="..." />` tanpa atribut `for` di dalam form view. Solusi yang diterapkan: diganti dengan `<div class="o_form_label text-muted">...</div>`.

---

## 12. Changelog

### Versi 14.2.0 (2026-03)

**Tambahan Baru:**
- ✅ Model `ins.faspe.consolidated.wizard` — wizard input multi-company
- ✅ Model `ins.faspe.consolidated.elimination.line` — konfigurasi eliminasi per company
- ✅ Model `ins.faspe.consolidated.report` — header laporan hasil konsolidasi
- ✅ Model `ins.faspe.consolidated.report.line` — baris detail laporan
- ✅ View wizard form dengan bagian periode, multi-company, dan eliminasi
- ✅ View laporan read-only dengan ringkasan dan tabel detail
- ✅ Menu **Laporan Keuangan FASPE** di bawah grup laporan akuntansi (`sequence=90`)
- ✅ Hak akses untuk 4 model baru (`account.group_account_user`)
- ✅ Validasi bisnis: min. 2 company, mata uang sama, konsistensi tanggal
- ✅ Baris check otomatis: Aset − (Liabilitas + Ekuitas)

### Versi 14.1.0 (sebelumnya)

- Versi dasar dengan General Ledger, Partner Ledger, Trial Balance, Partner Ageing, Financial Report
- Penambahan field `company_ids` (Many2many) di semua wizard report lama untuk dukungan multi-company

---

*Dokumen ini dibuat berdasarkan implementasi modul `account_dynamic_reports` versi 14.2.0 pada Odoo 14.0.*
