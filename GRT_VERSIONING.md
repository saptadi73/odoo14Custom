# GRT Addon Versioning

Gunakan pola `14.0.x.y.z` untuk addon custom GRT di Odoo 14.

- `14.0` mengikuti versi Odoo.
- `x` untuk rilis besar per modul jika ada perubahan fungsional besar atau milestone penting.
- `y` untuk fitur kecil atau penambahan perilaku yang tetap backward compatible.
- `z` untuk fix kecil, patch, atau penyesuaian teknis seperti CORS, domain, validasi, dan perbaikan bug.

Aturan praktis:

- Bugfix kecil: naikkan digit terakhir.
- Tambah endpoint, field, view, atau behavior baru yang kompatibel: naikkan digit ke-4 lalu reset digit terakhir jika perlu.
- Perubahan besar per modul boleh menaikkan digit ke-3.

Normalisasi yang sudah dilakukan:

- `grt_sales_business_category`: `14.0.1.0.12` setelah patch CORS.
- `grt_project_task`: `0.1` -> `14.0.0.1.0`.
- `grt_scada`: `7.2.1` -> `14.0.7.2.1` agar tetap membawa jejak versi lama dalam format Odoo-style.
