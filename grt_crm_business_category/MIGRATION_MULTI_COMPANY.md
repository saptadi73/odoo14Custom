# Migration Notes: Multi-Company

Perubahan multi-company pada modul ini menambahkan field wajib:

- `crm.business.category.company_id`
- `crm.stage.company_id`

Guard migrasi yang sudah ditambahkan:

- `crm.business.category.company_id` lama yang kosong akan diisi ke `base.main_company`.
- `crm.stage.company_id` lama yang kosong akan diambil dari `crm.team.company_id`, dan fallback ke `base.main_company`.

Hal yang tetap perlu diaudit sebelum upgrade produksi:

1. Category yang sebelumnya dipakai lintas company.
   Dampak:
   Setelah refactor, satu record category hanya boleh milik satu company.

2. Team/Lead/Stage lama yang memakai category dari company berbeda.
   Dampak:
   Data bisa tetap terbaca, tetapi akan kena validasi saat diedit.

3. User yang punya `default_business_category_id` atau `active_business_category_id` dari company yang tidak ada di `company_ids`.
   Dampak:
   Pilihan category user akan otomatis makin ketat setelah upgrade.

SQL audit yang disarankan sebelum upgrade:

```sql
-- Category yang dipakai oleh lebih dari satu company lewat lead
SELECT
    c.id,
    c.name,
    ARRAY_AGG(DISTINCT l.company_id) AS company_ids,
    COUNT(DISTINCT l.company_id) AS company_count
FROM crm_business_category c
JOIN crm_lead l ON l.business_category_id = c.id
GROUP BY c.id, c.name
HAVING COUNT(DISTINCT l.company_id) > 1;

-- Team dan category yang company-nya beda
SELECT
    t.id,
    t.name,
    t.company_id AS team_company_id,
    c.id AS category_id,
    c.name AS category_name,
    c.company_id AS category_company_id
FROM crm_team t
JOIN crm_business_category c ON c.id = t.business_category_id
WHERE t.company_id IS NOT NULL
  AND c.company_id IS NOT NULL
  AND t.company_id <> c.company_id;

-- Stage dan team yang company-nya beda
SELECT
    s.id,
    s.name,
    s.company_id AS stage_company_id,
    t.company_id AS team_company_id
FROM crm_stage s
JOIN crm_team t ON t.id = s.team_id
WHERE s.company_id IS NOT NULL
  AND t.company_id IS NOT NULL
  AND s.company_id <> t.company_id;

-- Lead dan category yang company-nya beda
SELECT
    l.id,
    l.name,
    l.company_id AS lead_company_id,
    c.id AS category_id,
    c.name AS category_name,
    c.company_id AS category_company_id
FROM crm_lead l
JOIN crm_business_category c ON c.id = l.business_category_id
WHERE l.company_id IS NOT NULL
  AND c.company_id IS NOT NULL
  AND l.company_id <> c.company_id;
```

Rekomendasi rollout:

1. Jalankan SQL audit di staging yang copy dari produksi.
2. Jika ada category dipakai lintas company, pecah category per company sebelum upgrade final.
3. Upgrade modul.
4. Uji create/edit lead, stage, pipeline, dan user access di tiap company.
