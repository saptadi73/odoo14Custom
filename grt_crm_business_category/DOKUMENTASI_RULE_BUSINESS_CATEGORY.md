# Dokumentasi Rule dan Implementasi CRM Business Category

## 1. Tujuan Modul
Modul `grt_crm_business_category` dipakai untuk memisahkan data CRM berdasarkan Business Category, agar:
- Pipeline bisa diikat ke kategori bisnis tertentu.
- Akses user dibatasi berdasarkan kategori yang diizinkan.
- User antar kategori tidak saling update data (kecuali admin/manager CRM).

## 2. Ringkasan Fitur yang Sudah Dibuat
1. Master model `crm.business.category`.
2. Seed data default 6 kategori business.
3. Field `business_category_id` pada:
- `crm.team` (pipeline/sales team) -> `required=True`.
- `crm.lead` (lead/opportunity).
4. Field user untuk kontrol akses kategori:
- `allowed_business_category_ids`
- `default_business_category_id`
- `active_business_category_id`
5. Rule security berbasis kategori (read/create/write/delete) sesuai role.
6. Menu konfigurasi khusus:
- `CRM > Configuration > Business Categories`
- `CRM > Configuration > Pipelines by Category`
- `CRM > Configuration > User Category Access`

## 3. Struktur Model
### 3.1 Model `crm.business.category`
Lokasi: `models/crm_business_category.py`
- `name` (unik)
- `code`
- `active`
- `description`

Constraint:
- `name` harus unik (`crm_business_category_name_uniq`).

### 3.2 Extend `crm.team`
Lokasi: `models/crm_team.py`
- Tambah `business_category_id` (`Many2one`, wajib, restrict).
- Default kategori diambil dari `env.user.active_business_category_id` atau `default_business_category_id`.
- Ada fallback aman saat migrasi schema (cek kolom DB dulu) agar tidak crash saat upgrade.

### 3.3 Extend `crm.lead`
Lokasi: `models/crm_lead.py`
- Tambah `business_category_id` (`Many2one`, restrict).
- Default kategori dari user active/default category (dengan fallback aman saat init).
- Onchange:
  - Jika `business_category_id` berubah dan tidak cocok dengan team, team di-reset.
  - Jika `team_id` dipilih dan team punya category, category lead otomatis mengikuti team.
- Constraint:
  - Team yang dipilih wajib punya business category.
  - Category lead harus cocok dengan category team.
  - Untuk type `lead` dan `opportunity`, business category wajib terisi.

### 3.4 Extend `res.users`
Lokasi: `models/res_users.py`
- `allowed_business_category_ids`: daftar kategori yang boleh diakses user.
- `default_business_category_id`: default kategori saat create record.
- `active_business_category_id`: kategori context aktif (mirip konsep active company).
- Onchange + constraint untuk jaga konsistensi:
  - Default/Active harus bagian dari Allowed.

### 3.5 Abstract Mixin
Lokasi: `models/business_category_mixin.py`
- `business.category.mixin` untuk dipakai ulang di modul lain.
- Menyediakan field `business_category_id` dengan default dari active/default category user.

## 4. Data Default
Lokasi: `data/crm_business_category_data.xml`
Dibuat 6 kategori awal:
- Business Category 1 (BC01)
- Business Category 2 (BC02)
- Business Category 3 (BC03)
- Business Category 4 (BC04)
- Business Category 5 (BC05)
- Business Category 6 (BC06)

## 5. Security dan Rule Akses

### 5.1 Access Control (`ir.model.access.csv`)
Lokasi: `security/ir.model.access.csv`
- `crm.group_use_lead`: read `crm.business.category`.
- `sales_team.group_sale_manager`: full access `crm.business.category`.

### 5.2 Record Rule (`ir.rule.csv`)
Lokasi: `security/ir.rule.csv`

#### Untuk user CRM biasa (`crm.group_use_lead`)
1. `crm.lead` read/create:
- Boleh baca dan create jika `business_category_id` termasuk `user.allowed_business_category_ids`.
2. `crm.lead` write/unlink:
- Boleh update/hapus hanya jika:
  - kategori termasuk allowed user, dan
  - record adalah milik user (`user_id = user.id`) atau dibuat oleh user (`create_uid = user.id`).
3. `crm.team`:
- Read-only untuk team di kategori yang diizinkan.
4. `crm.business.category`:
- Read-only kategori yang diizinkan.

#### Untuk manager/admin CRM (`sales_team.group_sale_manager`)
- Full access (read/write/create/unlink) untuk:
  - `crm.lead`
  - `crm.team`
  - `crm.business.category`

## 6. Menu dan Konfigurasi Operasional

### 6.1 Business Categories
Menu: `CRM > Configuration > Business Categories`
Fungsi: kelola master category.

### 6.2 Pipelines by Category
Menu: `CRM > Configuration > Pipelines by Category`
Fungsi: kelola `crm.team` beserta `business_category_id`.
Catatan: ini jalur utama untuk memastikan setiap pipeline punya category.

### 6.3 User Category Access
Menu: `CRM > Configuration > User Category Access`
Fungsi: set `Allowed`, `Default`, dan `Active` business category per user.

## 7. Alur Kerja yang Direkomendasikan
1. Buat/cek master kategori di menu Business Categories.
2. Set category pada setiap pipeline di menu Pipelines by Category.
3. Atur kategori user di menu User Category Access.
4. User operasional membuat lead/opportunity:
- Pilih Sales Team.
- Business Category otomatis mengikuti team.
- Constraint menjaga category-team tetap konsisten.

## 8. Catatan Teknis Penting
1. Di environment ini, inject ke tab default `Access Rights` user (`base.view_users_form`) sempat menimbulkan error validator `safe_eval` (opcode `RESUME/RETURN_CONST`).
2. Karena itu, pengaturan user kategori dibuat lewat menu terpisah `User Category Access` agar stabil.
3. Rule dipindah ke `ir.rule.csv` (bukan XML eval groups) untuk kompatibilitas environment saat ini.

## 9. Checklist Testing
1. Login sebagai manager CRM:
- Bisa lihat semua kategori/team/lead.
- Bisa create/edit/delete data lintas kategori.
2. Login sebagai user CRM biasa (category A):
- Hanya bisa lihat lead/team/category di category A.
- Tidak bisa edit lead milik user lain walau sama category.
- Bisa edit lead milik sendiri.
3. Buat lead dengan team tanpa category:
- Harus ditolak oleh constraint.
4. Ubah business category lead yang tidak cocok dengan team:
- Team harus reset / validasi menolak saat simpan.

## 10. File Inti Implementasi
- `__manifest__.py`
- `models/crm_business_category.py`
- `models/crm_team.py`
- `models/crm_lead.py`
- `models/res_users.py`
- `models/business_category_mixin.py`
- `security/ir.model.access.csv`
- `security/ir.rule.csv`
- `data/crm_business_category_data.xml`
- `views/crm_business_category_views.xml`
- `views/crm_team_business_category_views.xml`
- `views/res_users_business_category_views.xml`
