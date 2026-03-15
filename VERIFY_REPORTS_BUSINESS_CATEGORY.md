# Verifikasi Report Business Category

## 1) Upgrade Modul
Jalankan:

- `upgrade_business_category_reports.bat`

## 2) Verifikasi Menu Report

### Sales
- Menu: **Sales > Orders > Sales by Category**
- Cek tersedia view: Tree, Pivot, Graph
- Cek default grouping: `business_category_id`

### Purchase
- Menu: **Purchase > Purchases > Purchases by Category**
- Cek tersedia view: Tree, Pivot, Graph
- Cek default grouping: `business_category_id`

### Expense
- Menu: **Expenses > Expenses > Expenses by Category**
- Cek tersedia view: Tree, Pivot, Graph
- Cek default grouping: `business_category_id`

### Inventory
- Menu: **Inventory > Operations > Inventory by Category**
- Cek tersedia view: Tree, Pivot, Graph
- Cek default grouping: `business_category_id`

### CRM Pipeline
- Menu: **CRM > Reporting > Pipeline by Category**
- Cek domain otomatis: hanya `type = opportunity`
- Cek view: Tree, Pivot, Graph, Kanban, Form

### CRM Activity
- Menu: **CRM > Reporting > Activity History**
- Cek default grouping: `business_category_id`
- Cek view: Tree, Form, Pivot, Graph

## 3) Verifikasi Keamanan Akses
- Login sebagai user category A: pastikan data category B tidak muncul di report.
- Login sebagai user category B: pastikan data category A tidak muncul di report.
- Login sysadmin: boleh melihat semua sesuai company.

## 4) Validasi Cepat Runtime
Jalankan script:

- `python test_business_category_access_runtime.py`

Expected: semua skenario lintas category = **deny**.
