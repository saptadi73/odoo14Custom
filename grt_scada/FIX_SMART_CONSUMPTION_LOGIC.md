# Fix: Smart Consumption Calculation - Hindari Override dari Middleware

## Masalah
Ketika middleware mengirimkan nilai consumption yang berbeda dengan perhitungan BoM, Odoo akan otomatis override dengan nilai BoM calculation ketika MO di-mark done, terutama ketika parameter `auto_consume=True` (yang merupakan default).

## Root Cause
Di method `mark_mo_done()`, ada parameter `auto_consume` dengan default value `True`, yang menyebabkan sistem otomatis menjalankan `_auto_consume_from_bom()` dan mengupdate semua consumption berdasarkan perhitungan BoM, tanpa mempertimbangkan apakah consumption sudah ada dari middleware.

## Solusi
Implementasi **Smart Auto-Consume Logic** dengan dua perubahan utama:

### 1. Ubah Default `auto_consume` dari `True` → `False`

**File:**
- `middleware_service.py` (line 293)
- `scada_mo_data.py` (line 642)

**Sebelum:**
```python
auto_consume = payload_data.get('auto_consume', True)  # Default TRUE
```

**Sesudah:**
```python
auto_consume = payload_data.get('auto_consume', False)  # Default FALSE
```

### 2. Implementasi Method `_auto_consume_from_bom_smart()`

Method baru yang mengecek apakah consumption sudah ada sebelum auto-calculating:

```python
def _auto_consume_from_bom_smart(self, mo_record, equipment):
    """
    Smart auto-consume yang hanya consume jika consumption belum ada dari middleware/manual.
    
    Logic:
    - Untuk setiap material di BoM:
      1. Check apakah move.quantity_done sudah > 0 (ada update dari middleware atau manual)
      2. Jika sudah > 0, SKIP (jangan override) → source: 'skipped_existing'
      3. Jika 0, auto-calculate dan apply → source: 'auto_calculated'
    """
```

**Lokasi:**
- `middleware_service.py` (line 530-619)
- `scada_mo_data.py` (line 740-834)

## Behavior

### Sebelum (Problematic):
```
Middleware kirim: {mo_id: "WH/MO/00003", silo101: 1050, silo102: 480, ...}
  ↓
Odoo update consumption sesuai middleware
  ↓
Frontend call "mark_mo_done" dengan auto_consume=True (default)
  ↓
System override SEMUA consumption dengan BoM calculation
  ↓ 
❌ Result: Middleware data hilang, diganti BoM calculation
```

### Sesudah (Smart):
```
Middleware kirim: {mo_id: "WH/MO/00003", silo101: 1050, silo102: 480, ...}
  ↓
Odoo update consumption sesuai middleware
  ↓
Frontend call "mark_mo_done" dengan auto_consume=False (default)
  ↓
System check: "consumption > 0?" → YES → SKIP (keep middleware data)
  ↓
✅ Result: Middleware data preserved, tidak di-override
```

### Jika Ingin Auto-Consume Despite Existing Data:
```
Frontend bisa explicitly request: {auto_consume: true}
  ↓
System call _auto_consume_from_bom_smart()
  ↓
Check: "consumption > 0?" → YES → SKIP
  ↓
Check: "consumption = 0?" → YES → auto-calculate from BoM
```

## API Changes

### Endpoint: `POST /api/scada/mo/mark-done`

**Sebelum:**
```json
{
  "mo_id": "WH/MO/00003",
  "finished_qty": 20000,
  "auto_consume": true  // Default true - akan override middleware data
}
```

**Sesudah:**
```json
{
  "mo_id": "WH/MO/00003",
  "finished_qty": 20000,
  "auto_consume": false  // Default false - preserve middleware data
}
```

**Jika Ingin Tetap Auto-Calculate:**
```json
{
  "mo_id": "WH/MO/00003",
  "finished_qty": 20000,
  "auto_consume": true  // Explicit true - smart logic cek existing data
}
```

## Response Difference

### Response dengan Smart Logic:

```json
{
  "status": "success",
  "message": "Manufacturing order marked as done",
  "mo_id": "WH/MO/00003",
  "auto_consumed": 10,
  "materials": [
    {
      "material_code": "Pollard Angsa",
      "material_name": "Pollard Angsa",
      "quantity": 1050.0,
      "uom": "kg",
      "move_ids": [123],
      "source": "skipped_existing"  // ← NEW: menunjukkan data dari middleware/manual
    },
    {
      "material_code": "Mineral",
      "material_name": "Mineral",
      "quantity": 35.10,
      "uom": "kg",
      "move_ids": [456],
      "source": "auto_calculated"  // ← NEW: baru di-calculate dari BoM
    }
  ]
}
```

### Field `source` Bisa Berisi:
- `skipped_existing`: Consumption sudah ada dari middleware atau manual, tidak di-override
- `auto_calculated`: Consumption auto-calculated dari BoM karena belum ada sebelumnya

## Workflow Recommendation

### Skenario 1: Middleware-First (Recommended)
```
1. Middleware kirim update_mo_with_consumptions → quantity updated di Odoo
2. Frontend call mark_mo_done dengan auto_consume=false (default)
3. Result: Konsumsi dari middleware dipertahankan ✅
```

### Skenario 2: Manual Entry First  
```
1. User manual input consumption di Odoo
2. Frontend call mark_mo_done dengan auto_consume=false (default)
3. Result: Konsumsi manual dipertahankan ✅
```

### Skenario 3: Hybrid (Partial Manual, Partial BoM)
```
1. Middleware/User input BEBERAPA consumption
2. Frontend call mark_mo_done dengan auto_consume=true
3. System smart check:
   - Material dengan consumption > 0 → skip (keep existing)
   - Material dengan consumption = 0 → auto-calculate from BoM
4. Result: Hybrid approach, best of both ✅
```

## Files Modified

### 1. `/grt_scada/services/middleware_service.py`
- Line 293: Changed `auto_consume` default from `True` → `False`
- Line 296: Changed method call to `_auto_consume_from_bom_smart()`
- Line 530-619: Added new method `_auto_consume_from_bom_smart()`

### 2. `/grt_scada/models/scada_mo_data.py`
- Line 642: Changed `auto_consume` default from `True` → `False`
- Line 646: Changed method call to `_auto_consume_from_bom_smart()`
- Line 740-834: Added new method `_auto_consume_from_bom_smart()`

## Testing Checklist

- [ ] Middleware kirim consumption → check tidak ter-override saat mark_mo_done
- [ ] User manual input consumption → check tidak ter-override saat mark_mo_done
- [ ] auto_consume=false (default) → consumption preserved ✅
- [ ] auto_consume=true + existing consumption → smart check skip existing ✅
- [ ] auto_consume=true + no consumption → auto-calculate from BoM ✅
- [ ] Response include `source` field untuk tracking data origin

## Backward Compatibility

⚠️ **Breaking Change**: 
- Default `auto_consume` berubah dari `True` → `False`
- Middleware/client yang mengandalkan auto-consume sebelumnya perlu explicitly set `auto_consume: true`
- Jika tidak, consumption akan mengikuti middleware/manual input (yang merupakan desired behavior)

## Benefits

✅ **Preserve Middleware Data**: Consumption dari equipment/middleware tidak akan ter-override  
✅ **Smart Logic**: Hanya auto-calculate untuk material yang belum ada consumptionnya  
✅ **User Control**: Frontend bisa explicitly request auto-consume jika diperlukan  
✅ **Tracking**: Response menunjukkan source data (middleware vs BoM auto-calc)  
✅ **Backward Compatible**: Client bisa set `auto_consume: true` untuk tetap pakai old behavior  

## Related Endpoints

- `POST /api/scada/mo/update-with-consumptions` - Update consumption by equipment code
- `POST /api/scada/mo/mark-done` - Mark MO as done dengan smart auto-consume logic
- `POST /api/scada/material-consumption` - Apply material consumption

Sekarang consumption akan hanya mengikuti BoM otomatis jika TIDAK ada update dari middleware atau input manual! 🎉
