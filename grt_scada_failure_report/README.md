SCADA Failure Reporting
========================

Custom module untuk pencatatan laporan failure equipment SCADA.

Fitur
-----

- Model scada.failure.report
- Relasi equipment_code ke scada.equipment
- Field laporan: equipment_code, description, date
- Menu backend: SCADA > Failure Reporting > Failure Reports
- API input data (JSON)
- API report data untuk dashboard/chart
- Form input data (HTTP)

Struktur Data
-------------

Model: scada.failure.report

- equipment_code (many2one ke scada.equipment, required)
- description (text, required)
- date (datetime, required, default waktu saat create)

HTTP Routes
-----------

1. API JSON
~~~~~~~~~~~

POST /api/scada/failure-report

Auth: user session

Dokumentasi frontend yang lebih detail tersedia di:

- grt_scada_failure_report/FRONTEND_API_DOCUMENTATION.md

Contoh request dan response tersedia di file dokumentasi frontend.

2. Form Input
~~~~~~~~~~~~~

- GET /scada/failure-report/input untuk menampilkan form input
- POST /scada/failure-report/submit untuk submit form

3. API Report Dashboard
~~~~~~~~~~~~~~~~~~~~~~~

- GET/POST /api/scada/failure-report/report/kpi
- GET/POST /api/scada/failure-report/report/by-equipment
- GET/POST /api/scada/failure-report/report/timeline
- GET/POST /api/scada/failure-report/report/recent

Instalasi
---------

1. Update Apps List.
2. Install module SCADA Failure Reporting.
3. Pastikan module grt_scada sudah ter-install.
