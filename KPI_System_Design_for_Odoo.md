# KPI System Design for Odoo

## Overview

Dokumen ini menjelaskan desain sistem KPI yang dapat diimplementasikan sebagai custom module pada Odoo.

Tujuan sistem KPI:

* Mengukur performa karyawan
* Mengukur performa departemen
* Mengukur performa perusahaan
* Mengintegrasikan data performa dari modul ERP

Sistem KPI harus bersifat:

* dinamis
* scalable
* modular
* terintegrasi dengan modul ERP

---

# KPI Architecture

Struktur KPI mengikuti hierarki berikut:

Company KPI
↓
Department KPI
↓
Employee KPI
↓
KPI Value
↓
KPI Score

---

# KPI Entities

## KPI Department

Menyimpan daftar departemen perusahaan.

Contoh:

* Sales
* Finance
* IT
* Inventory
* Production

Field:

| Field       | Description     |
| ----------- | --------------- |
| id          | primary key     |
| name        | nama departemen |
| description | deskripsi       |

---

## KPI Definition

Master definisi KPI.

Contoh:

| KPI            | Department |
| -------------- | ---------- |
| Revenue        | Sales      |
| Repeat Order   | Sales      |
| Stock Accuracy | Inventory  |
| System Uptime  | IT         |

Field:

| Field              | Description |
| ------------------ | ----------- |
| code               | kode KPI    |
| name               | nama KPI    |
| department_id      | departemen  |
| kpi_type           | tipe KPI    |
| calculation_method | auto/manual |
| source_module      | modul ERP   |

---

## KPI Target

Target KPI dan bobot KPI.

Contoh:

| KPI          | Target    | Weight |
| ------------ | --------- | ------ |
| Revenue      | 100000000 | 40     |
| Repeat Order | 20        | 20     |

---

## KPI Target History

Digunakan untuk menyimpan perubahan target setiap tahun.

---

## KPI Period

Menentukan periode evaluasi KPI.

Contoh:

| Year | Month |
| ---- | ----- |
| 2025 | 01    |
| 2025 | 02    |

Status:

* draft
* open
* closed

---

## KPI Assignment

Mapping KPI ke employee.

Contoh:

| Employee | KPI          |
| -------- | ------------ |
| Sales A  | Revenue      |
| Sales A  | Repeat Order |

---

## KPI Value

Nilai KPI aktual.

Nilai KPI dapat berasal dari:

* modul Sales
* modul CRM
* modul Inventory
* modul Manufacturing
* input manual

---

## KPI Score

Skor KPI yang dihitung dari nilai KPI.

Formula dasar:

score = (actual_value / target_value) × weight

---

## KPI Team

Menyimpan tim kerja.

Contoh:

* Sales Team A
* Warehouse Team
* Production Team

---

## KPI Team Score

Skor KPI untuk tim.

---

## KPI Evidence

Bukti pencapaian KPI.

Contoh:

* laporan
* dokumen
* foto

---

# KPI Calculation Flow

1. Modul ERP menghasilkan event

contoh:

Sales Order Confirmed

2. Sistem menyimpan nilai KPI

insert ke table kpi_value

3. Cron job menghitung score

calculate_kpi_score()

4. Score disimpan ke table kpi_score

---

# Odoo Module Structure

Disarankan membuat module:

odoo_kpi

Struktur:

odoo_kpi
│
├── models
│   ├── kpi_definition.py
│   ├── kpi_assignment.py
│   ├── kpi_value.py
│   ├── kpi_score.py
│   └── kpi_team.py
│
├── views
│   ├── kpi_definition_view.xml
│   ├── kpi_dashboard.xml
│
├── security
│   └── ir.model.access.csv
│
└── data
└── kpi_cron.xml

---

# Cron Job

Cron digunakan untuk menghitung KPI.

Schedule:

* daily
* monthly

Function:

calculate_kpi_score()

---

# KPI Dashboard

Dashboard menampilkan:

Employee KPI

* KPI achievement
* score
* grade

Department KPI

* average score
* top performer
* bottom performer

Company KPI

* department ranking
* total score

---

# Security Role

Role yang disarankan:

KPI Admin
KPI Manager
Employee

---

# Future Extension

Sistem KPI dapat dikembangkan menjadi:

* Balanced Scorecard
* AI KPI prediction
* KPI gamification
* KPI forecasting
