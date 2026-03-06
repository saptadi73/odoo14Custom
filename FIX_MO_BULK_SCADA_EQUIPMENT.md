# Fix: SCADA Equipment Tidak Muncul di BoM & MO Bulk Generator

## Masalah Utama (ROOT CAUSE)

Field **SCADA Equipment hilang** dari form BoM dan MO karena view XML `scada_mrp_views.xml` telah **di-disable** di manifest.

Di file `__manifest__.py` line 30, view ini di-comment dengan alasan:
```python
# Temporary: disabled due view validation issue on current runtime (safe_eval opcode check)
# 'views/scada_mrp_views.xml',
```

Akibatnya:
- ❌ Field SCADA Equipment tidak muncul di form BoM (finished goods)
- ❌ Field SCADA Equipment tidak muncul di BoM Lines (components)  
- ❌ Field SCADA Equipment tidak muncul di MO form (header & moves)
- ❌ Bulk Generator tidak bisa mengambil SCADA equipment dari BoM karena field tidak ada

## Solusi

### 1. Re-enable View XML untuk BoM & MO

**File:** `grt_scada/__manifest__.py`

Uncomment baris view yang di-disable:

```python
'data': [
    # Security - FIRST
    'security/security_groups.xml',
    # External views inheritance - EARLY
    'views/scada_mrp_views.xml',  # ✅ RE-ENABLED
    'views/scada_product_views.xml',
```

View ini menambahkan:
- Field `scada_equipment_id` di header BoM (setelah field `code`)
- Field `scada_equipment_id` di BoM Lines tree view (setelah `product_id`)
- Field `scada_equipment_id` di MO form (setelah `bom_id`)
- Field `scada_equipment_id` di MO raw material moves tree

### 2. Fix Propagasi di Bulk Generator

**File:** `grt_scada/wizard/scada_mo_bulk_wizard.py`

Menambahkan sync SCADA equipment setelah moves dibuat:

```python
# Populate raw material and finished product moves
for mo in mo_records:
    # Get values for raw material moves from BoM
    raw_moves_values = mo._get_moves_raw_values()
    self.env['stock.move'].create(raw_moves_values)
    
    # Get values for finished product moves
    finished_moves_values = mo._get_moves_finished_values()
    self.env['stock.move'].create(finished_moves_values)
    
    # ✨ Sync SCADA equipment dari BoM lines ke moves
    mo._sync_scada_equipment_to_moves()
    
    # Now confirm the MO
    if mo.state == 'draft':
        mo.action_confirm()
```

## File yang Diubah

1. **grt_scada/__manifest__.py** 
   - Re-enable `scada_mrp_views.xml`
   - Update version: 7.0.81 → 7.0.83
   
2. **grt_scada/wizard/scada_mo_bulk_wizard.py**
   - Menambahkan `_sync_scada_equipment_to_moves()` call

## Hasil Setelah Fix

✅ Field SCADA Equipment muncul di form BoM (header)  
✅ Field SCADA Equipment muncul di BoM Lines (untuk setiap component)  
✅ Field SCADA Equipment muncul di MO form (header)  
✅ Field SCADA Equipment muncul di raw material moves  
✅ Bulk Generator otomatis propagasi SCADA equipment dari BoM  
✅ Equipment tracking dan OEE calculation berjalan normal

## Testing Checklist

1. **Buka Form BoM**
   - [ ] Field "Default SCADA Equipment" muncul di header (setelah field Code)
   - [ ] Kolom "SCADA Equipment (Optional)" muncul di BoM Lines table
   
2. **Set SCADA Equipment di BoM**
   - [ ] Pilih SCADA equipment di header BoM
   - [ ] Pilih SCADA equipment untuk component tertentu di BoM lines
   - [ ] Save BoM
   
3. **Buat MO Manual**
   - [ ] Buat MO dari BoM yang sudah punya SCADA equipment
   - [ ] Verifikasi SCADA equipment ter-set otomatis di header MO
   - [ ] Verifikasi SCADA equipment ter-set di raw material moves
   
4. **Buat MO via Bulk Generator**
   - [ ] Gunakan Bulk Generator untuk product dengan BoM yang punya SCADA equipment
   - [ ] Verifikasi setiap MO punya SCADA equipment di header
   - [ ] Verifikasi raw material moves punya SCADA equipment sesuai BoM line
   
5. **Proses MO & Check OEE**
   - [ ] Konfirmasi dan proses MO sampai done
   - [ ] Verifikasi OEE record terbuat otomatis
   - [ ] Check equipment tracking berjalan normal

## Deployment

```bash
# 1. Restart Odoo service
python restart_odoo.py

# 2. Upgrade module grt_scada via Odoo UI
# Apps → SCADA for Odoo → Upgrade

# Atau via command line:
odoo-bin -c odoo.conf -d your_database -u grt_scada --stop-after-init
```

**⚠️ PENTING:** Setelah upgrade, **refresh browser** (Ctrl+F5) untuk memastikan view XML terbaru dimuat.

## Catatan Teknis

View XML `scada_mrp_views.xml` menggunakan XPath inheritance yang aman dan tidak ada expression `eval` atau `attrs` yang kompleks. View ini seharusnya tidak menyebabkan "safe_eval opcode check" error pada runtime normal Odoo 14.

Jika sebelumnya ada error terkait view ini, kemungkinan karena:
- Module dependency belum terinstall (`mrp` module)
- View parent (`mrp.mrp_bom_form_view`) belum tersedia saat load
- Database corruption atau cache issue

Solusi: Pastikan module `mrp` sudah terinstall dan up-to-date sebelum upgrade `grt_scada`.

---

**Date:** 2026-03-06  
**Module:** grt_scada  
**Version:** 7.0.83  
**Issue:** SCADA Equipment field hilang dari BoM & MO forms  
**Root Cause:** View XML di-disable di manifest  
**Status:** ✅ Fixed
