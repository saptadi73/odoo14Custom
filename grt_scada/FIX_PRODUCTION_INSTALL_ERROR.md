# Fix: Installation Error in Production Server - grt_scada Module

## Masalah
Saat menginstall modul `grt_scada` di server production, terjadi error:
```
Exception: Pemasangan modul grt_scada gagal: berkas grt_scada/security/ir.model.access.csv tidak dapat diproses:
No matching record found for id eksternal 'model_scada_quality_control' in field 'Model'
No matching record found for id eksternal 'model_scada_equipment_oee' in field 'Model'
No matching record found for id eksternal 'model_scada_equipment_oee_line' in field 'Model'
No matching record found for id eksternal 'model_scada_equipment_failure' in field 'Model'
Kurang value yang dibutuhkan untuk field 'Model' (model_id)
```

## Penyebab
Error terjadi karena **urutan loading file data di `__manifest__.py`** tidak tepat:

1. File `security/ir.model.access.csv` di-load **SEBELUM** models yang direferensikannya terdaftar di tabel `ir.model`
2. Meskipun models sudah didefinisikan di Python (`models/*.py`), Odoo belum mendaftarkan mereka ke database hingga proses instalasi selesai
3. Ini menciptakan masalah "chicken-and-egg": access rules membutuhkan model yang belum terdaftar

## Solusi

### 1. Tambah File `security/ir_model.xml`
Membuat file baru yang mendefinisikan models secara eksplisit di database:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="0">
        <record id="model_scada_equipment" model="ir.model">
            <field name="name">SCADA Equipment</field>
            <field name="model">scada.equipment</field>
            <field name="state">manual</field>
        </record>
        
        <record id="model_scada_sensor_reading" model="ir.model">
            <field name="name">SCADA Sensor Reading</field>
            <field name="model">scada.sensor.reading</field>
            <field name="state">manual</field>
        </record>
        
        <!-- ... dan model-model lainnya -->
    </data>
</odoo>
```

### 2. Update Urutan Loading di `__manifest__.py`
Mengubah urutan file data agar models terdaftar SEBELUM access rules di-load:

**SEBELUM:**
```python
'data': [
    'security/security_groups.xml',
    'security/ir.model.access.csv',  # ❌ Di-load terlalu awal
    'security/ir.rule.xml',
    'views/scada_equipment_view.xml',
    # ... views lainnya
],
```

**SESUDAH:**
```python
'data': [
    'security/security_groups.xml',
    'security/ir_model.xml',  # ✅ Daftar models dulu
    # Views di-load sebelum access rules
    'views/scada_equipment_view.xml',
    'views/scada_mrp_views.xml',
    'views/scada_sensor_reading_view.xml',
    'views/scada_api_log_view.xml',
    'views/scada_quality_control_view.xml',
    'views/scada_equipment_oee_view.xml',
    'views/scada_equipment_failure_view.xml',
    # Security files setelah views
    'security/ir.model.access.csv',  # ✅ Sekarang models sudah ada
    'security/ir.rule.xml',
    'views/menu.xml',
    # ... file lainnya
],
```

### 3. Update Version
Version dinaikkan dari `6.0.51` ke `6.0.52`

## Models yang Didefinisikan

File `security/ir_model.xml` mendefinisikan models berikut:
- `scada.equipment`
- `scada.sensor.reading`
- `scada.api.log`
- `scada.equipment.material`
- `scada.mo.weight`
- `scada.quality.control`
- `scada.equipment.oee`
- `scada.equipment.oee.line`
- `scada.equipment.failure`

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
- ✅ File `ir_model.xml` menggunakan `noupdate="0"` agar bisa di-update
- ✅ Urutan loading yang benar memastikan semua dependencies terpenuhi
- ⚠️ Jika modul sudah ter-install sebelumnya, **upgrade** modul untuk menerapkan perubahan:
  ```bash
  odoo-bin -c /etc/odoo/odoo.conf -d database_name -u grt_scada --stop-after-init
  ```

## Testing

Setelah perbaikan, modul dapat di-install tanpa error di:
- ✅ Local development environment
- ✅ Production server dengan Odoo 14

## Files Modified

1. `grt_scada/__manifest__.py` - Update loading order dan version
2. `grt_scada/security/ir_model.xml` - File baru untuk definisi models

## References

- Odoo Documentation: [Module Manifest](https://www.odoo.com/documentation/14.0/developer/reference/addons/manifest.html)
- Odoo Documentation: [Security](https://www.odoo.com/documentation/14.0/developer/reference/addons/security.html)
