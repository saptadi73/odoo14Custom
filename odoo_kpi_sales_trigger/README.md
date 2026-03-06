# Odoo KPI Sales Trigger

## Overview

Modul `odoo_kpi_sales_trigger` digunakan untuk membuat `KPI Value` otomatis dari transaksi Sales Order berdasarkan perilaku pembayaran customer.

Fokus utama modul ini adalah memberi score KPI kepada salesperson berdasarkan:

- pembayaran tepat waktu
- keterlambatan pembayaran berdasarkan jumlah hari
- nilai transaksi di atas threshold tertentu

Modul ini terintegrasi dengan:

- `odoo_kpi`
- `sale_management`
- `account`
- `grt_sales_business_category`

---

# Objective

Tujuan modul ini:

- mengukur kualitas penjualan, bukan hanya jumlah transaksi
- memberi reward untuk transaksi yang dibayar tepat waktu
- memberi penalti untuk transaksi yang terlambat dibayar
- memberi bonus untuk transaksi dengan nilai besar
- mengirim hasil perhitungan ke `kpi.value` berdasarkan `kpi.assignment`

---

# Business Logic

Setiap Sales Order yang sudah lunas penuh akan dievaluasi.

Sistem akan:

1. mengambil Sales Order
2. mengecek apakah semua invoice customer terkait sudah `paid`
3. mengambil tanggal pelunasan terakhir
4. mengambil tanggal jatuh tempo invoice
5. menghitung `late_days`
6. mencari `KPI Sales Trigger Rule` yang cocok
7. membuat atau meng-update `kpi.value`

---

# Score Formula

Rumus score per `Trigger Line`:

```text
score = on_time_score - (late_days x late_penalty_per_day)
```

Kemudian:

- score tidak boleh lebih kecil dari `minimum_score`
- jika `amount_total >= transaction_amount_threshold`, maka score ditambah `transaction_bonus_score`

Formula final:

```text
score = max(on_time_score - (late_days x late_penalty_per_day), minimum_score)
if amount_total >= transaction_amount_threshold:
    score += transaction_bonus_score
```

---

# Trigger Event

KPI tidak dibuat saat quotation dibuat atau saat Sales Order dikonfirmasi.

KPI dibuat saat transaksi sudah benar-benar lunas.

Event yang dipantau:

- `account.payment.action_post()`
- perubahan `account.move.payment_state` menjadi `paid`

Ini dipilih agar KPI merepresentasikan realisasi pembayaran, bukan sekadar penjualan.

---

# Data Flow

Flow modul:

```text
Customer Payment Posted
        |
        v
Invoice becomes Paid
        |
        v
Find linked Sale Order
        |
        v
Check Business Category + Salesperson + Assignment Period
        |
        v
Calculate KPI Score
        |
        v
Create / Update KPI Value
```

---

# Rule Structure

Model utama:

- `kpi.sales.trigger.rule`
- `kpi.sales.trigger.rule.line`

## kpi.sales.trigger.rule

Header rule dipakai untuk:

- nama rule
- sequence
- status active
- `business_category_id`

Rule dibuat per business category agar scoring dapat dibedakan untuk tiap kategori bisnis.

## kpi.sales.trigger.rule.line

Setiap line menentukan scoring untuk satu employee dan satu assignment KPI.

Field penting:

- `employee_id`
- `assignment_id`
- `on_time_score`
- `late_penalty_per_day`
- `minimum_score`
- `transaction_amount_threshold`
- `transaction_bonus_score`
- `source_module`
- `note`

Constraint:

- `employee_id` pada line harus sama dengan `employee_id` pada `assignment_id`

---

# Payment and Late Day Calculation

## Fully Paid

Sales Order dianggap selesai untuk evaluasi KPI jika:

- memiliki invoice customer (`out_invoice`) yang sudah `posted`
- semua invoice customer terkait memiliki `payment_state = paid`

## Payment Completion Date

Tanggal pelunasan yang dipakai adalah tanggal pelunasan terakhir dari invoice yang terkait dengan Sales Order.

Jika satu Sales Order memiliki beberapa invoice, maka sistem mengambil tanggal pembayaran paling akhir.

## Due Date

Tanggal jatuh tempo yang dipakai adalah tanggal jatuh tempo paling akhir dari invoice customer terkait.

Jika `invoice_date_due` tidak ada, sistem memakai `invoice_date`.

## Late Days

```text
late_days = payment_completion_date - due_date
```

Jika pembayaran dilakukan sebelum atau sama dengan jatuh tempo, maka `late_days = 0`.

---

# KPI Output

Output modul ini adalah record di model `kpi.value`.

Field yang diisi:

- `assignment_id`
- `value`
- `source_module`
- `reference_model`
- `reference_id`

Modul menggunakan mekanisme upsert:

- jika KPI untuk kombinasi assignment + reference + source sudah ada, maka nilai di-update
- jika belum ada, maka dibuat record baru

Ini mencegah duplikasi KPI saat event pembayaran terpanggil lebih dari sekali.

---

# Example Configuration

Contoh rule untuk salesperson A:

- `on_time_score`: `10`
- `late_penalty_per_day`: `1`
- `minimum_score`: `0`
- `transaction_amount_threshold`: `100000000`
- `transaction_bonus_score`: `5`

## Scenario 1

- nilai transaksi: `80.000.000`
- telat: `0` hari

Perhitungan:

```text
score = max(10 - (0 x 1), 0) = 10
```

Hasil:

- score `10`

## Scenario 2

- nilai transaksi: `80.000.000`
- telat: `3` hari

Perhitungan:

```text
score = max(10 - (3 x 1), 0) = 7
```

Hasil:

- score `7`

## Scenario 3

- nilai transaksi: `120.000.000`
- telat: `0` hari

Perhitungan:

```text
score = max(10 - (0 x 1), 0) + 5 = 15
```

Hasil:

- score `15`

## Scenario 4

- nilai transaksi: `120.000.000`
- telat: `20` hari

Perhitungan:

```text
score = max(10 - (20 x 1), 0) + 5 = 5
```

Hasil:

- score `5`

---

# Setup in Odoo

Langkah konfigurasi:

1. pastikan modul `odoo_kpi`, `grt_sales_business_category`, dan `odoo_kpi_sales_trigger` sudah terinstall
2. buat `KPI Definition` pada modul KPI
3. buat `KPI Period`
4. buat `KPI Assignment` untuk employee sales
5. buka menu `Sales > KPI Sales Triggers`
6. buat rule per `Business Category`
7. tambahkan `Trigger Lines` untuk setiap salesperson
8. isi parameter score sesuai kebijakan perusahaan

---

# Recommended Master Data Setup

Agar modul berjalan dengan benar, sebaiknya:

- setiap salesperson memiliki relasi `res.users` ke `hr.employee`
- Sales Order memiliki `business_category_id`
- invoice berasal dari Sales Order yang sama
- KPI Assignment dibuat untuk periode aktif
- period KPI mencakup tanggal pelunasan transaksi

---

# Assumptions

Asumsi implementasi saat ini:

- score diberikan ke salesperson pada `sale.order.user_id`
- evaluasi dilakukan saat order lunas penuh
- invoice yang dihitung hanya `out_invoice`
- refund belum dijadikan trigger KPI terpisah
- bonus nilai transaksi bersifat tambahan di atas score dasar

---

# Limitation

Batasan implementasi saat ini:

- belum ada pembeda rule berdasarkan team sales
- belum ada pembeda rule berdasarkan produk atau product category
- belum ada tier threshold bertingkat dalam satu line
- belum ada wizard simulasi score dari transaksi
- belum ada scheduled recompute untuk data historis

Jika dibutuhkan, pengembangan berikutnya bisa menambahkan:

- multi-threshold bonus
- penalty maksimum
- rule per sales team
- rule per customer segment
- recompute KPI existing transaction

---

# Technical Notes

Hook utama ada di:

- `models/account_payment.py`
- `models/account_move.py`
- `models/sale_order.py`
- `models/kpi_sales_trigger_rule.py`

Logika inti:

- mendeteksi invoice customer yang telah lunas
- menelusuri Sales Order terkait
- menghitung score berdasarkan konfigurasi
- menulis hasil ke `kpi.value`

---

# Security

Akses konfigurasi rule diberikan ke:

- `odoo_kpi.group_kpi_manager`
- `odoo_kpi.group_kpi_admin`
- `sales_team.group_sale_manager`

---

# Upgrade Module

Contoh command upgrade:

```bat
c:\odoo14c\python\python.exe C:\odoo14c\server\odoo-bin -c C:\addon14\odoo.conf -d kanjabung_MRP -u odoo_kpi_sales_trigger --stop-after-init
```

Atau gunakan script:

```bat
upgrade_odoo_kpi_sales_trigger.bat
```

---

# Testing Checklist

Checklist test manual:

1. buat KPI assignment untuk salesperson
2. buat rule pada business category yang sesuai
3. buat Sales Order dengan salesperson tersebut
4. konfirmasi Sales Order dan generate invoice
5. lakukan pembayaran sebelum due date
6. pastikan `kpi.value` terbentuk dengan score sesuai
7. ulangi dengan pembayaran terlambat
8. ulangi dengan nilai transaksi di atas threshold
9. pastikan tidak ada duplikasi `kpi.value` untuk order yang sama

---

# Summary

`odoo_kpi_sales_trigger` menambahkan mekanisme KPI sales berbasis kualitas pembayaran customer.

Dengan modul ini, KPI sales tidak hanya menghitung volume penjualan, tetapi juga:

- ketepatan pembayaran
- dampak keterlambatan pembayaran
- nilai strategis transaksi
