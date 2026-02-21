# CRITICAL: Production Installation Fix for grt_scada

## Error: Model not found (scada.quality.control, etc.)

Jika Anda mendapat error seperti ini saat install di production:
```
ValidationError: Model tidak ditemukan: scada.quality.control
ValidationError: Model tidak ditemukan: scada.equipment.oee
ValidationError: Model tidak ditemukan: scada.equipment.failure
```

## Root Cause

Error ini terjadi karena **Python files belum ter-reload** setelah update files di production server. Odoo masih menggunakan Python bytecode (.pyc) yang lama atau module yang masih ada di memory.

## ✅ SOLUSI LENGKAP - Step by Step

### 1. Update Files di Production Server

```bash
cd /opt/odoo14/custom-addons/grt_scada
git pull origin main
```

### 2. **PENTING**: Hapus Python Cache

```bash
# Hapus semua .pyc files
find /opt/odoo14/custom-addons/grt_scada -name "*.pyc" -delete
find /opt/odoo14/custom-addons/grt_scada -name "__pycache__" -type d -exec rm -rf {} +

# Atau gunakan find dengan -delete (lebih aman)
find /opt/odoo14/custom-addons/grt_scada -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
```

### 3. **WAJIB**: Restart Odoo Server

```bash
# Untuk systemd
sudo systemctl restart odoo
# atau
sudo systemctl restart odoo14

# Untuk service
sudo service odoo restart

# Verifikasi restart berhasil
sudo systemctl status odoo
```

### 4. Update Apps List di Odoo

Login ke Odoo:
1. Pergi ke **Apps**
2. Klik **Update Apps List**  
3. Konfirmasi update

### 5. Install/Upgrade Module

#### Opsi A: Via UI (Recommended)
1. Search "SCADA" di Apps
2. Klik **Install** (untuk fresh install) atau **Upgrade** (untuk update)

#### Opsi B: Via Command Line
```bash
# Fresh install
/opt/odoo14/odoo-bin -c /etc/odoo/odoo.conf -d your_database -i grt_scada --stop-after-init

# Upgrade existing installation
/opt/odoo14/odoo-bin -c /etc/odoo/odoo.conf -d your_database -u grt_scada --stop-after-init

# Kemudian restart lagi
sudo systemctl restart odoo
```

## Troubleshooting

### Jika Masih Error Setelah Langkah Di Atas

1. **Cek apakah file Python ada:**
```bash
ls -la /opt/odoo14/custom-addons/grt_scada/models/scada_quality_control.py
ls -la /opt/odoo14/custom-addons/grt_scada/models/scada_equipment_oee.py
ls -la /opt/odoo14/custom-addons/grt_scada/models/scada_equipment_failure.py
```

2. **Cek Python syntax errors:**
```bash
python3 -m py_compile /opt/odoo14/custom-addons/grt_scada/models/scada_quality_control.py
python3 -m py_compile /opt/odoo14/custom-addons/grt_scada/models/scada_equipment_oee.py
```

3. **Cek Odoo logs:**
```bash
sudo tail -f /var/log/odoo/odoo.log
# atau
sudo journalctl -u odoo -f
```

4. **Cek permissions:**
```bash
sudo chown -R odoo:odoo /opt/odoo14/custom-addons/grt_scada
sudo chmod -R 755 /opt/odoo14/custom-addons/grt_scada
```

5. **Force clear all cache:**
```bash
# Stop Odoo
sudo systemctl stop odoo

# Clear ALL .pyc files in Odoo
find /opt/odoo14 -name "*.pyc" -delete
find /opt/odoo14 -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Start Odoo
sudo systemctl start odoo
```

## Mengapa Ini Terjadi?

1. **Python bytecode caching**: Python menyimpan .pyc files untuk performance. File ini tidak auto-update saat source code berubah
2. **Odoo module registry**: Odoo cache module information di memory. Perlu restart untuk reload
3. **Loading order**: Views di-load sebelum models jika server tidak fresh restart

## Manifest Loading Order (v6.0.55)

```python
'data': [
    'security/security_groups.xml',
    # Views dan UI dulu
    'views/scada_equipment_view.xml',
    'views/scada_mrp_views.xml',
    'views/scada_sensor_reading_view.xml',
    'views/scada_api_log_view.xml',
    'views/scada_quality_control_view.xml',
    'views/scada_equipment_oee_view.xml',
    'views/scada_equipment_failure_view.xml',
    'views/menu.xml',
    # Data files
    'data/demo_data.xml',
    'data/ir_cron.xml',
    # Reports
    'reports/scada_quality_control_report.xml',
    'reports/scada_equipment_oee_report.xml',
    # Security access rules TERAKHIR
    'security/ir.model.access.csv',
    'security/ir.rule.xml',
],
```

## Best Practice untuk Update Module di Production

### Checklist Lengkap

- [ ] Backup database sebelum update
- [ ] `git pull origin main` untuk update files
- [ ] Hapus Python cache (*.pyc dan __pycache__)
- [ ] **RESTART Odoo server** (WAJIB!)
- [ ] Update Apps List di Odoo UI
- [ ] Install/Upgrade module
- [ ] Test functionality
- [ ] Monitor logs untuk errors

### Script Automation (Optional)

Buat script untuk automate proses:

```bash
#!/bin/bash
# update_grt_scada.sh

set -e  # Exit on error

echo "=== Updating grt_scada module ==="

# 1. Update files
cd /opt/odoo14/custom-addons/grt_scada
git pull origin main

# 2. Clear Python cache
echo "Clearing Python cache..."
find . -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 3. Set permissions
echo "Setting permissions..."
sudo chown -R odoo:odoo /opt/odoo14/custom-addons/grt_scada
sudo chmod -R 755 /opt/odoo14/custom-addons/grt_scada

# 4. Restart Odoo
echo "Restarting Odoo..."
sudo systemctl restart odoo

# 5. Wait for Odoo to start
echo "Waiting for Odoo to start..."
sleep 10

echo "=== Update complete! ==="
echo "Now go to Odoo UI and:"
echo "1. Update Apps List"
echo "2. Upgrade grt_scada module"
```

## Summary

**TL;DR**: Saat update module di production:
1. ✅ `git pull`
2. ✅ Clear .pyc cache
3. ✅ **RESTART Odoo** (most important!)
4. ✅ Update Apps List
5. ✅ Install/Upgrade module

**Jangan skip step 3 (restart)** - ini yang paling sering dilupakan dan menyebabkan error "Model not found"!
