# Odoo KPI Customer Behavior Trigger

## Overview

Modul `odoo_kpi_customer_behavior_trigger` digunakan untuk membuat `kpi.value` otomatis berdasarkan hasil segmentasi perilaku pelanggan dari modul customer behavior.

Tujuan utamanya adalah menghubungkan kualitas portofolio pelanggan milik salesperson dengan sistem KPI. Dengan pendekatan ini, salesperson tidak hanya dinilai dari transaksi yang terjadi, tetapi juga dari kondisi pelanggan yang mereka tangani.

Contoh kebijakan yang bisa diterapkan:

- pelanggan `repeat` memberi score tambahan
- pelanggan `reactivated` memberi score positif
- pelanggan `at_risk` mulai memberi pengurangan
- pelanggan `inactive` memberi pengurangan lebih besar
- pelanggan `dormant` memberi pengurangan lebih berat
- pelanggan `lost` memberi penalti paling besar

Modul ini terintegrasi dengan:

- `odoo_kpi`
- `grt_sales_business_category`
- `sale_management`
- `hr`

---

# Objective

Tujuan modul ini:

- memberi KPI berdasarkan kualitas relasi pelanggan
- memberi insentif untuk mempertahankan pelanggan aktif dan repeat order
- memberi penalti saat pelanggan mulai memburuk sampai hilang
- menghubungkan hasil customer behavior ke `kpi.assignment`
- menghasilkan `kpi.value` secara otomatis dari data analisis customer behavior

---

# Business Logic

Setiap kali `customer.behavior.analysis` dibuat atau diperbarui, sistem akan mengevaluasi apakah hasil analisis tersebut perlu dikonversi menjadi nilai KPI.

Sistem akan:

1. membaca hasil analisis perilaku pelanggan
2. mengambil segment customer
3. mengambil business category dari analisis
4. mencari salesperson yang bertanggung jawab atas customer tersebut
5. mencari `KPI Customer Behavior Trigger Rule` yang cocok
6. mencocokkan segment dengan rule line
7. membuat atau meng-update `kpi.value`

---

# Trigger Event

Trigger KPI dijalankan saat record `customer.behavior.analysis`:

- dibuat (`create`)
- diperbarui (`write`) pada field penting

Field yang memicu proses ulang:

- `segment_id`
- `business_category_id`
- `partner_id`
- `analysis_date`

Sumber event biasanya berasal dari:

- cron `Daily Customer Behavior Analysis`
- wizard recompute customer behavior
- pemanggilan manual `compute_customer_behavior()`

---

# Data Flow

Flow modul:

```text
Customer Behavior Analysis Created / Updated
                |
                v
Read Customer Segment + Business Category
                |
                v
Find Responsible Salesperson
                |
                v
Match KPI Behavior Trigger Rule
                |
                v
Create / Update KPI Value
```

---

# Rule Structure

Model utama:

- `kpi.customer.behavior.trigger.rule`
- `kpi.customer.behavior.trigger.rule.line`

## kpi.customer.behavior.trigger.rule

Header rule digunakan untuk:

- nama rule
- sequence
- status active
- `business_category_id`

Rule dibuat per `Business Category` agar score perilaku pelanggan dapat dipisahkan antar lini bisnis.

## kpi.customer.behavior.trigger.rule.line

Setiap line menentukan score untuk kombinasi:

- segment pelanggan
- employee
- KPI assignment

Field penting:

- `segment_id`
- `employee_id`
- `assignment_id`
- `score_value`
- `source_module`
- `note`

Nilai `score_value` boleh:

- positif untuk reward
- negatif untuk penalti
- nol jika hanya ingin menandai segment tertentu tanpa dampak score

Constraint:

- `employee_id` pada line harus sama dengan `employee_id` pada `assignment_id`

---

# Segment Scoring

Modul ini tidak mengunci formula matematis seperti KPI payment trigger. Score ditentukan langsung per segment.

Contoh konfigurasi:

- `repeat` = `+5`
- `reactivated` = `+3`
- `at_risk` = `-2`
- `inactive` = `-4`
- `dormant` = `-6`
- `lost` = `-10`

Dengan model ini, perusahaan bisa bebas menentukan kebijakan scoring sendiri sesuai strategi customer retention.

---

# Employee Resolution Logic

Salesperson yang akan menerima KPI dicari dengan urutan berikut:

1. `partner.user_id`
2. salesman dari Sales Order terakhir customer pada `business_category_id` yang sama

Penjelasan:

- jika partner sudah memiliki salesperson tetap pada field `user_id`, maka salesperson tersebut dipakai
- jika tidak ada, sistem mencari Sales Order terakhir customer dalam kategori bisnis yang sama
- jika tetap tidak ditemukan employee yang valid, KPI tidak dibuat

Relasi ke employee dilakukan melalui mapping `res.users -> hr.employee`.

---

# KPI Output

Output modul ini adalah record pada model `kpi.value`.

Field yang ditulis:

- `assignment_id`
- `value`
- `source_module`
- `reference_model`
- `reference_id`

Mekanisme yang dipakai adalah upsert:

- jika kombinasi assignment + source + reference sudah ada, nilai di-update
- jika belum ada, record baru dibuat

Ini penting untuk mencegah duplikasi saat analisis customer dijalankan berulang pada hari yang sama.

---

# Reference Model

Untuk membedakan sumber data KPI, modul ini menggunakan:

```text
reference_model = customer.behavior.analysis.rule.line.<line_id>
reference_id = <analysis_id>
```

Dengan pola ini:

- satu hasil analisis customer hanya menghasilkan satu KPI value per line rule
- update analisis yang sama tidak membuat duplikasi

---

# Example Configuration

Contoh kebijakan untuk salesperson A:

- `repeat` = `+5`
- `reactivated` = `+3`
- `at_risk` = `-2`
- `inactive` = `-4`
- `dormant` = `-6`
- `lost` = `-10`

## Scenario 1

Customer masuk segment `repeat`

Hasil:

- KPI value `+5`

## Scenario 2

Customer masuk segment `reactivated`

Hasil:

- KPI value `+3`

## Scenario 3

Customer masuk segment `at_risk`

Hasil:

- KPI value `-2`

## Scenario 4

Customer masuk segment `inactive`

Hasil:

- KPI value `-4`

## Scenario 5

Customer masuk segment `dormant`

Hasil:

- KPI value `-6`

## Scenario 6

Customer masuk segment `lost`

Hasil:

- KPI value `-10`

---

# Setup in Odoo

Langkah konfigurasi:

1. pastikan modul `odoo_kpi`, `grt_sales_business_category`, dan `odoo_kpi_customer_behavior_trigger` sudah terinstall
2. pastikan data segment customer behavior sudah tersedia
3. buat `KPI Definition` untuk KPI customer behavior
4. buat `KPI Period`
5. buat `KPI Assignment` untuk masing-masing salesperson
6. buka menu `Sales > Customer Behavior > KPI Customer Behavior Triggers`
7. buat rule per `Business Category`
8. tambahkan line untuk setiap segment yang ingin diberi score
9. isi `score_value` sesuai kebijakan perusahaan

---

# Recommended Master Data Setup

Agar modul berjalan dengan benar, sebaiknya:

- setiap salesperson memiliki relasi `res.users` ke `hr.employee`
- partner customer memiliki `user_id` jika ada owner tetap
- sales order customer tersimpan dengan benar pada business category yang relevan
- KPI assignment tersedia untuk periode aktif
- cron customer behavior berjalan normal

---

# Integration with Customer Behavior Module

Modul ini bergantung pada hasil dari `grt_sales_business_category`, khususnya model:

- `customer.behavior.analysis`
- `customer.behavior.segment`
- `res.partner.customer_segment_id`

Artinya, kualitas output KPI sepenuhnya bergantung pada kualitas analisis customer behavior yang sudah ada.

Jika segment customer belum terhitung, maka KPI behavior juga belum bisa dibuat.

---

# Assumptions

Asumsi implementasi saat ini:

- satu hasil analisis customer menghasilkan satu KPI value per line rule yang cocok
- score diberikan ke satu salesperson yang dianggap paling relevan
- business category pada analisis menjadi filter utama rule
- score per segment bersifat statis, tidak dihitung dari formula tambahan

---

# Limitation

Batasan implementasi saat ini:

- belum mendukung pembagian score ke lebih dari satu salesperson
- belum mendukung weighting tambahan berdasarkan total amount customer
- belum mendukung scoring berdasarkan perubahan segment dari bulan sebelumnya
- belum ada simulasi dampak segment ke KPI
- belum ada recompute KPI historis terpisah dari recompute customer behavior

Pengembangan lanjutan yang mungkin:

- score berbeda berdasarkan total revenue customer
- score berbeda berdasarkan jumlah repeat order
- penalty tambahan jika customer turun beberapa level sekaligus
- rule berbasis team sales
- snapshot trend segment per period KPI

---

# Technical Notes

Hook utama ada di:

- `models/customer_behavior_analysis.py`
- `models/kpi_customer_behavior_trigger_rule.py`

Logika utama:

- intercept create dan write pada `customer.behavior.analysis`
- cari employee yang relevan
- cari rule yang cocok berdasarkan business category dan segment
- kirim hasil ke `kpi.value`

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
c:\odoo14c\python\python.exe C:\odoo14c\server\odoo-bin -c C:\addon14\odoo.conf -d kanjabung_MRP -u odoo_kpi_customer_behavior_trigger --stop-after-init
```

---

# Testing Checklist

Checklist test manual:

1. buat KPI assignment untuk salesperson
2. buat rule customer behavior pada business category yang sesuai
3. atur score per segment
4. jalankan analisis customer behavior
5. pastikan customer yang `repeat` membuat `kpi.value` positif
6. pastikan customer yang `at_risk` atau lebih buruk membuat `kpi.value` negatif
7. pastikan analisis ulang tidak membuat duplikasi KPI value
8. pastikan employee yang menerima score sesuai owner customer atau sales order terakhir

---

# Summary

`odoo_kpi_customer_behavior_trigger` menambahkan KPI trigger berbasis kualitas perilaku pelanggan.

Dengan modul ini, sistem KPI sales dapat menangkap sinyal penting seperti:

- pelanggan yang loyal dan repeat
- pelanggan yang menurun kualitasnya
- pelanggan yang sudah dorman atau lost

Ini membuat KPI sales lebih dekat ke objective retensi pelanggan, bukan hanya transaksi sesaat.
