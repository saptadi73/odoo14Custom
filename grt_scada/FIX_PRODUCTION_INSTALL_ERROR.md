# Fix: Installation Error in Production Server - grt_scada Module

## Masalah Awal: Models Not Found
Saat menginstall modul `grt_scada` di server production, terjadi error:
```
Exception: Pemasangan modul grt_scada gagal: berkas grt_scada/security/ir.model.access.csv tidak dapat diproses:
No matching record found for id eksternal 'model_scada_quality_control' in field 'Model'
No matching record found for id eksternal 'model_scada_equipment_oee' in field 'Model'
No matching record found for id eksternal 'model_scada_equipment_oee_line' in field 'Model'
No matching record found for id eksternal 'model_scada_equipment_failure' in field 'Model'
```

## Error yang Muncul Saat Troubleshooting

### Error 2: Field Type Cannot Be Modified
```
UserError: Field "Type" tidak dapat dimodifikasi pada model.
ParseError: while parsing /opt/odoo14/custom-addons/grt_scada/security/ir_model.xml:6
```

### Error 3: Model Name Must Start with 'x_'
```
ValidationError: Nama model harus dimulai dengan 'x_'.
ParseError: while parsing /opt/odoo14/custom-addons/grt_scada/security/ir_model.xml:32
```

## Penyebab Root Cause

Error terjadi karena **urutan loading file data di `__manifest__.py`** tidak tepat:

1. File `security/ir.model.access.csv` di-load **SEBELUM** models yang direferensikannya terdaftar
2. Models yang didefinisikan di Python **otomatis terdaftar oleh Odoo** saat module di-load
3. Masalahnya adalah timing: access rules di-load sebelum Odoo sempat register models dari views

## ❌ Solusi yang SALAH (v6.0.52-6.0.53)

Awalnya mencoba membuat file `security/ir_model.xml` untuk mendefinisikan models secara manual. **Ini SALAH** karena:

- ❌ Models yang didefinisikan di Python (`models.Model`) **tidak boleh** dibuat manual di XML
- ❌ Odoo akan menganggap ini sebagai custom model yang harus dimulai dengan `x_`
- ❌ Menyebabkan ValidationError dan conflict dengan auto-registration

## ✅ Solusi yang BENAR (v6.0.54)

**Cukup ubah urutan loading di `__manifest__.py`** - TANPA file `ir_model.xml`!
## ✅ Solusi yang BENAR (v6.0.54)

**Cukup ubah urutan loading di `__manifest__.py`** - TANPA file `ir_model.xml`!

### Urutan Loading yang Benar

**SEBELUM (SALAH):**
```python
'data': [
    'security/security_groups.xml',
    'security/ir.model.access.csv',  # ❌ Di-load terlalu awal
    'security/ir.rule.xml',
    'views/scada_equipment_view.xml',
    # ... views lainnya
],
```

**SESUDAH (BENAR):**
```python
'data': [
    'security/security_groups.xml',
    # ✅ Views di-load DULU - models auto-register saat views di-parse
    'views/scada_equipment_view.xml',
    'views/scada_mrp_views.xml',
    'views/scada_sensor_reading_view.xml',
    'views/scada_api_log_view.xml',
    'views/scada_quality_control_view.xml',
    'views/scada_equipment_oee_view.xml',
    'views/scada_equipment_failure_view.xml',
    # ✅ Security files setelah views - models sudah terdaftar
    'security/ir.model.access.csv',
    'security/ir.rule.xml',
    'views/menu.xml',
    'data/demo_data.xml',
    'data/ir_cron.xml',
    'reports/scada_quality_control_report.xml',
    'reports/scada_equipment_oee_report.xml',
],
```

### Mengapa Ini Bekerja?

1. **Models defined in Python auto-register**: Saat Odoo load module Python files, models otomatis terdaftar di `ir.model`
2. **Views trigger model registration**: Saat views di-parse, Odoo memastikan models yang direferensikan sudah ada
3. **Access rules needs registered models**: CSV access rules membutuhkan model sudah terdaftar di `ir.model`

### Poin Penting

- ✅ **TIDAK PERLU** file `ir_model.xml`
- ✅ **CUKUP** ubah urutan: views → access rules
- ✅ Models didefinisikan di Python akan **auto-register**
- ❌ **JANGAN** manual create record `ir.model` untuk Python-defined models
```

### Version History
- `6.0.51`: Versi awal dengan error (access rules sebelum views)
- `6.0.52`: ❌ Salah - Tambah `ir_model.xml` (menyebabkan error baru)
- `6.0.53`: ❌ Salah - Update `ir_model.xml` (masih error)
- `6.0.54`: ✅ **BENAR** - Hapus `ir_model.xml`, cukup reorder loading

## Models yang Terdaftar Otomatis

Models berikut didefinisikan di Python dan **auto-register** oleh Odoo:
- `scada.equipment` → [models/scada_equipment.py](models/scada_equipment.py)
- `scada.sensor.reading` → [models/scada_sensor_reading.py](models/scada_sensor_reading.py)
- `scada.api.log` → [models/scada_api_log.py](models/scada_api_log.py)
- `scada.equipment.material` → [models/scada_equipment_material.py](models/scada_equipment_material.py)
- `scada.mo.weight` → [models/scada_mo_weight.py](models/scada_mo_weight.py)
- `scada.quality.control` → [models/scada_quality_control.py](models/scada_quality_control.py)
- `scada.equipment.oee` → [models/scada_equipment_oee.py](models/scada_equipment_oee.py)
- `scada.equipment.oee.line` → [models/scada_equipment_oee.py](models/scada_equipment_oee.py)
- `scada.equipment.failure` → [models/scada_equipment_failure.py](models/scada_equipment_failure.py)

## Cara Install di Production Server

1. **Update modul di server:**
   ```bash
   cd /path/to/addons/grt_scada
   git pull origin main
   ```

2. **Restart Odoo service:**
   ```bash
   sudo systemctl restart odoo
   # atau
   sudo service odoo restart
   ```

3. **Install modul dari UI:**
   - Login ke Odoo
   - Pergi ke Apps
   - Update Apps List
   - Cari "SCADA"
   - Klik Install

4. **Atau install via command line:**
   ```bash
   odoo-bin -c /etc/odoo/odoo.conf -d database_name -i grt_scada --stop-after-init
   ```

## Catatan Penting

- ✅ Perbaikan ini **backward compatible** - tidak akan merusak instalasi yang sudah ada
- ✅ **Solusi sederhana**: Hanya ubah urutan loading, tanpa file tambahan
- ✅ Models Python **auto-register** - tidak perlu definisi manual di XML
- ✅ Urutan yang benar: security groups → views → access rules
- ⚠️ Jika modul sudah ter-install sebelumnya, **upgrade** modul untuk menerapkan perubahan:
  ```bash
  odoo-bin -c /etc/odoo/odoo.conf -d database_name -u grt_scada --stop-after-init
  ```

## Testing

Setelah perbaikan versi 6.0.54, modul dapat di-install tanpa error di:
- ✅ Local development environment
- ✅ Production server dengan Odoo 14
- ✅ Fresh install
- ✅ Upgrade dari versi sebelumnya

## Files Modified

**Version 6.0.54 (Final Fix):**
1. `grt_scada/__manifest__.py` - Reorder data loading (views before access rules)
2. ~~`grt_scada/security/ir_model.xml`~~ - **DELETED** (not needed)

## Lessons Learned

1. **Models defined in Python don't need XML definitions** in `ir.model`
2. **Loading order matters**: Views must load before security access rules
3. **Manual ir.model creation** for Python models causes ValidationError
4. **Keep it simple**: The simplest solution (reordering) is often the correct one

## References

- Odoo Documentation: [Module Manifest](https://www.odoo.com/documentation/14.0/developer/reference/addons/manifest.html)
- Odoo Documentation: [Security](https://www.odoo.com/documentation/14.0/developer/reference/addons/security.html)
