# Technical Notes GRT MRP Overhead Costing

Dokumen ini ditujukan untuk developer, implementor, dan admin Odoo yang perlu memahami struktur modul secara teknis.

## Nama Modul

- `grt_mrp_overhead_costing`

## Tujuan Teknis

Modul ini menambahkan mekanisme overhead absorption bulanan di Odoo Manufacturing dengan fitur:

- master `mrp.overhead.type`
- dokumen bulanan `mrp.overhead.period`
- line per overhead `mrp.overhead.period.line`
- hasil alokasi per MO `mrp.overhead.allocation.line`
- integrasi dengan `hr.expense`, `account.move`, `account.move.line`, dan `mrp.production`
- integrasi `stock.valuation.layer` untuk kapitalisasi overhead ke inventory valuation

## Model Utama

### `mrp.overhead.type`

Master jenis overhead.

Field kunci:

- `allocation_basis`: `kg`, `hour`, `mo`
- `capitalize_to_inventory`: absorbsi overhead diarahkan ke akun valuation produk jadi (fallback ke absorption account)
- `default_source_account_id`
- `absorption_account_id`
- `variance_account_id`

### `mrp.overhead.period`

Dokumen bulanan.

Field kunci:

- `date_start`
- `date_end`
- `journal_id`
- `state`
- `line_ids`
- `allocation_line_ids`
- `adjustment_move_id`

Method penting:

- `action_initialize_lines()`
- `action_load_source_entries()`
- `action_compute_overhead()`
- `action_create_adjustment_move()`
- `action_reset_to_draft()`

### `mrp.overhead.period.line`

Line overhead per periode.

Field kunci:

- `allocation_basis`
- `capitalize_to_inventory`
- `rate_mode`
- `manual_rate`
- `manual_actual_amount`
- `source_move_line_ids`
- `allocation_line_ids`
- `actual_amount`
- `basis_qty`
- `rate`
- `absorbed_amount`
- `variance_amount`

Method penting:

- `_assign_source_move_lines()`
- `_get_basis_qty_for_production()`
- `_get_weight_for_production()`
- `_get_hours_for_production()`
- `_get_source_distribution()`
- `_validate_accounts_for_adjustment()`

### `mrp.overhead.allocation.line`

Penyimpanan applied overhead per MO.

Field kunci:

- `production_id`
- `basis_qty`
- `rate`
- `applied_amount`

## Integrasi Model Existing

### `hr.expense`

Field tambahan:

- `mrp_overhead_type_id`

Tujuan:

- menandai expense sebagai actual overhead

### `hr.expense.sheet`

Field tambahan:

- `mrp_overhead_type_id`

Saat `action_sheet_move_create()`, field overhead diteruskan ke journal entry.

### `account.move`

Field tambahan:

- `mrp_overhead_type_id`
- `mrp_overhead_period_id`

Tujuan:

- menandai jurnal actual overhead dan jurnal adjustment

### `account.move.line`

Field tambahan:

- `mrp_overhead_type_id`
- `mrp_overhead_period_id`
- `mrp_overhead_period_line_id`

Tujuan:

- memudahkan penjodohan actual overhead ke overhead line pada periode tertentu

### `mrp.production`

Field tambahan:

- `currency_id`
- `overhead_allocation_line_ids`
- `overhead_applied_amount`
- `overhead_applied_count`

## Basis Alokasi

### `kg`

Basis menggunakan qty produksi MO.

Implementasi:

- prioritas `qty_produced` jika ada
- fallback ke qty finished move
- fallback ke `product_qty`

### `hour`

Basis menggunakan jam produksi.

Implementasi:

- prioritas `workorder.duration`
- fallback `workorder.duration_expected`
- fallback `date_start` ke `date_finished`

Catatan:

- jika workorder tidak ada dan `date_start` kosong, hasil basis = `0`

### `mo`

Basis selalu `1` per MO.

## Mekanisme Compute

Saat `action_compute_overhead()` dipanggil:

1. line overhead diinisialisasi jika belum ada
2. source journal items ditarik dari `account.move.line`
3. allocation line lama dihapus
4. MO done dalam periode dicari
5. basis per MO dihitung
6. total basis per line dihitung
7. rate dihitung
   - `manual_rate` jika `rate_mode = manual`
   - `actual_amount / total_basis` jika `rate_mode = auto`
8. applied amount dibuat per MO

## Mekanisme Jurnal Adjustment

Saat `action_create_adjustment_move()` dipanggil:

Untuk setiap line overhead yang punya nilai:

1. actual overhead direverse dari akun sumber
2. absorbed overhead didebit ke akun absorpsi
   - jika `capitalize_to_inventory` aktif dan ada allocation line, debit diarahkan ke akun valuation produk jadi per alokasi MO
   - fallback ke `absorption_account_id` jika akun valuation tidak tersedia
3. variance diposting ke akun variance jika ada

## Mekanisme Stock Valuation Layer (SVL)

Saat `action_create_adjustment_move()` dipanggil dan line overhead memiliki `capitalize_to_inventory = True`:

1. sistem membuat SVL revaluation (`quantity = 0`) per allocation line MO
2. nilai `value` SVL mengikuti `applied_amount` per MO
3. SVL di-link ke:
   - period (`mrp_overhead_period_id`)
   - period line (`mrp_overhead_period_line_id`)
   - allocation line (`mrp_overhead_allocation_line_id`)
   - MO (`mrp_production_id`)
4. jika field tersedia di model SVL, `account_move_id` diarahkan ke jurnal adjustment

Catatan kontrol:

- `action_reset_to_draft()` diblokir jika SVL overhead sudah terbentuk untuk menjaga konsistensi valuation history.

Jurnal dibuat `draft` agar bisa direview oleh finance.

## Urutan Manifest Yang Aman

Urutan load yang saat ini dipakai:

1. `security/ir.model.access.csv`
2. `data/sequence.xml`
3. `views/mrp_overhead_type_views.xml`
4. `views/mrp_overhead_period_views.xml`
5. `views/mrp_production_views.xml`
6. `views/hr_expense_views.xml`
7. `views/mrp_overhead_menu_views.xml`

Alasan:

- access harus ada lebih dulu
- sequence/data aman diload sebelum pemakaian
- action dan view utama dibuat lebih dulu
- inherited views dibaca setelah model siap
- menu paling akhir agar parent/action sudah ada

## Catatan Implementasi Di Database Saat Ini

Kondisi implementasi terbaru:

- `Listrik Produksi` basis `kg`
- `SDM Produksi` basis `kg`
- akun absorpsi dan variance custom sudah dibuat
- periode Februari 2026 pernah dipakai untuk test hitung dan jurnal

## File Terkait

- `grt_mrp_overhead_costing/__manifest__.py`
- `grt_mrp_overhead_costing/models/mrp_overhead_type.py`
- `grt_mrp_overhead_costing/models/mrp_overhead_period.py`
- `grt_mrp_overhead_costing/models/mrp_production.py`
- `grt_mrp_overhead_costing/models/hr_expense.py`
- `grt_mrp_overhead_costing/models/account_move.py`
- `grt_mrp_overhead_costing/views/mrp_overhead_type_views.xml`
- `grt_mrp_overhead_costing/views/mrp_overhead_period_views.xml`
- `grt_mrp_overhead_costing/views/mrp_production_views.xml`
- `grt_mrp_overhead_costing/views/hr_expense_views.xml`
- `grt_mrp_overhead_costing/views/mrp_overhead_menu_views.xml`

## Saran Pengembangan Selanjutnya

Beberapa improvement yang mungkin berguna:

- wizard setup awal
- laporan variance per periode
- report applied overhead per MO / per produk
- validasi otomatis agar expense overhead wajib ditag
- integrasi analytic account per overhead type
- menu dokumentasi internal di Odoo
