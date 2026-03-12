# DEPLOYMENT & VERIFICATION GUIDE
# SILO OEE Equipment Fix - grt_scada Module

## Issue Yang Diperbaiki
- ✅ SILO equipment sekarang akan menampilkan OEE records dari `scada.equipment.oee.line` (detail level)
- ✅ Main PLC terus menampilkan OEE records dari header level (tidak ada perubahan)

## Modified File
- `grt_scada/controllers/main.py` 
  - Function: `get_oee_equipment_avg()` [around line 980-990]
  - Change: Added fallback untuk count OEE line records jika header OEE count = 0

## Deployment Checklist

### ✅ Pre-Deployment
- [ ] File `main.py` sudah di-edit lokal
- [ ] Syntax validation sudah OK (python -m py_compile)
- [ ] Backup original file jika perlu

### 🚀 DEPLOYMENT STEPS

#### Step 1: Upload File ke Server
```bash
# Option A: Via SCP (recommended)
scp /path/to/grt_scada/controllers/main.py user@kanjabung.web.id:/opt/odoo/addons/grt_scada/controllers/

# Option B: Via SFTP (WinSCP, FileZilla)
# Connect to server, navigate to /opt/odoo/addons/grt_scada/controllers/
# Upload main.py file

# Option C: Via Git (if repo is synced)
git push origin main  # on local
# Then pull on server
```

#### Step 2: Restart Odoo Service
```bash
# Login ke server
ssh user@kanjabung.web.id

# Restart Odoo (gunakan salah satu)
sudo systemctl restart odoo14
# atau
sudo /etc/init.d/odoo14 restart
# atau
sudo supervisorctl restart odoo

# Tunggu 30 detik, kemudian cek status
sudo systemctl status odoo14
# Pastikan: Active (running)
```

#### Step 3: Upgrade Module di Odoo UI
1. Login ke Odoo: https://kanjabung.web.id
2. Go to **Apps** menu (hamburger icon top-left)
3. Search bar: type "grt_scada"
4. Click on **SCADA** module
5. Click **Upgrade** button (top-right)
6. Tunggu sampai status berubah jadi "Installed"

#### Step 4: Verify Deployment
```powershell
# Run test script setelah restart selesai
cd c:\addon14
.\test_silo_oee_after_deployment.ps1
```

Expected output:
```
✓ Authentication successful
✓ API call successful

Equipment with OEE Data:
  • SILO A (silo101)
    - OEE Records: XXX
    - Avg Yield: YY.YY%
  
  • Main PLC - Injection Machine 01 (plc01)
    - OEE Records: 64
    - Avg Yield: 100.0%

SILO equipment with data: 1+
LQ equipment with data: 1+
PLC equipment with data: 1+

✓ SUCCESS: SILO equipment sekarang muncul dengan OEE records!
```

## Rollback (Jika Ada Masalah)
```bash
# Restore original file
# Restart Odoo
sudo systemctl restart odoo14
# Upgrade module di UI
```

## Support Info
- Server: https://kanjabung.web.id
- Database: kanjabung_MRP
- Module: grt_scada
- Date Range: 2026-02-24 to 2026-03-13
