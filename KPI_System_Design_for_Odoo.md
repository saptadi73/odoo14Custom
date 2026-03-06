# KPI System Design for Odoo

## Overview

Dokumen ini menjelaskan desain sistem KPI yang dapat digunakan sebagai modul custom pada Odoo.

Sistem KPI digunakan untuk:

* mengukur performa karyawan
* mengukur performa departemen
* mengukur performa perusahaan
* mengambil data KPI dari modul ERP

Sistem harus bersifat:

* dinamis
* modular
* scalable
* terintegrasi dengan ERP

---

# KPI Architecture

Hierarchy KPI:

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

# Entities

## KPI Department

Menyimpan daftar departemen.

Contoh:

Sales
Finance
Inventory
IT

---

## KPI Definition

Master definisi KPI.

Contoh:

Revenue
Repeat Order
Inventory Accuracy
System Uptime

Field utama:

* code
* name
* department_id
* source_module

---

## KPI Target

Target KPI dan bobot KPI.

Contoh:

Revenue target = 100000000
Weight = 40%

---

## KPI Target History

Digunakan untuk menyimpan perubahan target setiap tahun.

---

## KPI Period

Periode evaluasi KPI.

Contoh:

2025-01
2025-02

Status:

draft
open
closed

---

## KPI Assignment

Mapping KPI ke employee.

Contoh:

Sales A → Revenue
Sales A → Repeat Order

Assignment menentukan:

* KPI apa yang dimiliki employee
* target KPI
* weight KPI

---

## KPI Value

Nilai KPI aktual.

KPI value selalu terhubung ke assignment.

Field utama:

assignment_id
value
source_module
reference_model
reference_id

Contoh:

assignment_id = 10
value = 15000000
reference_model = sale.order

---

## KPI Score

Hasil agregasi KPI.

Formula dasar:

score = (actual_value / target_value) × weight

---

## KPI Team

Digunakan untuk mengelompokkan employee.

Contoh:

Sales Team A
Warehouse Team

---

## KPI Team Score

Score KPI pada level tim.

---

## KPI Evidence

Bukti pencapaian KPI.

Contoh:

laporan
dokumen
foto

---

# KPI Data Flow

ERP Event

↓

Insert KPI Value

↓

Aggregate KPI Score

↓

Update KPI Score Table

---

# Example ERP Integration

Sales Module

Event:

Sales Order Confirmed

↓

Insert KPI Value (Revenue KPI)

---

Inventory Module

Event:

Stock Move Completed

↓

Insert KPI Value (Stock Accuracy KPI)

---

Manufacturing Module

Event:

Production Finished

↓

Insert KPI Value (Production Output KPI)

---

# Odoo Module Structure

Custom module:

odoo_kpi

Structure:

odoo_kpi
│
├── models
│   ├── kpi_definition.py
│   ├── kpi_assignment.py
│   ├── kpi_value.py
│   ├── kpi_score.py
│   ├── kpi_team.py
│
├── views
│   ├── kpi_definition_view.xml
│   ├── kpi_assignment_view.xml
│   ├── kpi_dashboard.xml
│
├── security
│   └── ir.model.access.csv
│
└── data
└── kpi_cron.xml

---

# KPI Calculation

Cron job menghitung KPI score.

schedule:

daily
monthly

Function:

calculate_kpi_score()

---

# Security Role

Role yang disarankan:

KPI Admin
KPI Manager
Employee

---

# Advantages

Dynamic KPI configuration
ERP integrated
Scalable architecture
Audit trail support
Supports employee and team KPI
