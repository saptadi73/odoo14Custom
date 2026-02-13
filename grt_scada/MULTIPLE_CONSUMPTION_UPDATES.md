# Multiple Consumption Updates untuk MO yang Belum Di-Mark Done

## Pertanyaan
Untuk MO yang belum di-mark done, apakah consumed masih bisa di-update dari middleware lagi?

## Jawaban
**YA, BISA!** Consumption dapat di-update multiple times dari middleware selama MO belum di-mark done (state ≠ 'done'/'cancel').

## Behavior

### Saat MO Status = Confirmed/In Progress (belum done):
✅ Bisa update consumption multiple times  
✅ Support ADD mode (accumulating)  
✅ Support REPLACE mode (set value baru)  

### Saat MO Status = Done atau Cancel:
❌ Tidak bisa update consumption lagi  
❌ Return error: "Cannot update consumption for MO in done state"  

## Ada 2 Mode Update

### 1. ADD Mode (Default)
```
Behavior: Menambahkan ke existing consumption (accumulating)

Update 1: equipment_id="silo101", quantity=100
  → quantity_done = 100

Update 2: equipment_id="silo101", quantity=50 (ADD mode)
  → quantity_done = 100 + 50 = 150 ✓ Accumulate

Use case: Equipment send incremental updates, misal:
  - 08:00: sent 100 kg
  - 09:00: sent another 50 kg (total 150)
  - 10:00: sent another 75 kg (total 225)
```

### 2. REPLACE Mode (Baru)
```
Behavior: Mengganti existing consumption dengan value baru (tidak accumulate)

Update 1: equipment_id="silo101", quantity=100, update_mode="replace"
  → quantity_done = 100

Update 2: equipment_id="silo101", quantity=120, update_mode="replace"
  → quantity_done = 120 ✓ Replace (bukan 220)

Update 3: equipment_id="silo101", quantity=115, update_mode="replace"
  → quantity_done = 115 ✓ Replace (bukan 235)

Use case: Equipment send actual consumption at different times:
  - 08:00: actual consumption = 100 kg
  - 09:00: revised to 120 kg (measurement correction)
  - 10:00: revised to 115 kg (final correction)
```

## API Usage Examples

### Endpoint: POST /api/scada/material-consumption

#### Contoh 1: ADD Mode (Default)
```bash
curl -X POST http://localhost:8069/api/scada/material-consumption \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "equipment_id": "silo101",
    "mo_id": "WH/MO/00003",
    "product_id": 123,
    "quantity": 100,
    "update_mode": "add"
  }'

Response:
{
  "status": "success",
  "message": "Material consumption added to MO moves",
  "mo_id": "WH/MO/00003",
  "mo_state": "confirmed",
  "applied_qty": 100,
  "update_mode": "add",
  "can_update_again": true,  ← Masih bisa update lagi!
  "move_ids": [123]
}

# Update kedua (ADD 50 ke 100)
curl -X POST http://localhost:8069/api/scada/material-consumption \
  -d '{
    "equipment_id": "silo101",
    "mo_id": "WH/MO/00003",
    "product_id": 123,
    "quantity": 50,
    "update_mode": "add"
  }'

Result: quantity_done = 100 + 50 = 150 ✓
```

#### Contoh 2: REPLACE Mode
```bash
curl -X POST http://localhost:8069/api/scada/material-consumption \
  -d '{
    "equipment_id": "silo101",
    "mo_id": "WH/MO/00003",
    "product_id": 123,
    "quantity": 100,
    "update_mode": "replace"
  }'

Response: quantity_done = 100

# Update kedua (REPLACE 100 dengan 120)
curl -X POST http://localhost:8069/api/scada/material-consumption \
  -d '{
    "equipment_id": "silo101",
    "mo_id": "WH/MO/00003",
    "product_id": 123,
    "quantity": 120,
    "update_mode": "replace"
  }'

Result: quantity_done = 120 ✓ (bukan 220)
```

#### Contoh 3: Batch Update via update-with-consumptions
```bash
# Material consumption by equipment code - multiple times
curl -X POST http://localhost:8069/api/scada/mo/update-with-consumptions \
  -d '{
    "mo_id": "WH/MO/00003",
    "silo101": 100,
    "silo102": 50,
    "silo103": 200
  }'

# Update lagi (ADD default)
curl -X POST http://localhost:8069/api/scada/mo/update-with-consumptions \
  -d '{
    "mo_id": "WH/MO/00003",
    "silo101": 50,      # ADD: 100 + 50 = 150
    "silo102": 25,      # ADD: 50 + 25 = 75
    "silo104": 75       # New: 75
  }'
```

## Response Fields

```json
{
  "status": "success",
  "message": "Material consumption added to MO moves",
  "mo_id": "WH/MO/00003",
  "mo_state": "confirmed",
  "applied_qty": 100,
  "update_mode": "add",              // ← Mode yang dipakai
  "can_update_again": true,          // ← Bisa update lagi?
  "move_ids": [123, 124]
}
```

### Response Field: can_update_again
- `true` = MO masih belum done, bisa update consumption lagi
- `false` = MO sudah done/cancel, tidak bisa update lagi

## Workflow Skenario

### Skenario 1: Incremental Updates (ADD mode)
```
Timeline:
08:00 - Equipment start, send initial consumption
  POST /api/scada/material-consumption {quantity: 100}
  → quantity_done = 100

09:00 - Production continue, send update
  POST /api/scada/material-consumption {quantity: 75, update_mode: "add"}
  → quantity_done = 100 + 75 = 175

10:00 - Production done, send final consumption
  POST /api/scada/material-consumption {quantity: 50, update_mode: "add"}
  → quantity_done = 175 + 50 = 225

11:00 - Mark MO as done
  POST /api/scada/mo/mark-done {finished_qty: 20000, auto_consume: false}
  → consumed = 225 kg ✓
```

### Skenario 2: Revised/Corrected Values (REPLACE mode)
```
Timeline:
08:00 - Equipment send actual consumption
  POST /api/scada/material-consumption {quantity: 100, update_mode: "replace"}
  → quantity_done = 100

09:00 - Measurement correction from equipment
  POST /api/scada/material-consumption {quantity: 105, update_mode: "replace"}
  → quantity_done = 105 ✓ (replace 100)

10:00 - Final correction
  POST /api/scada/material-consumption {quantity: 103, update_mode: "replace"}
  → quantity_done = 103 ✓ (replace 105)

11:00 - Mark MO as done
  POST /api/scada/mo/mark-done {finished_qty: 20000, auto_consume: false}
  → consumed = 103 kg ✓ (final corrected value)
```

### Szenario 3: Hybrid (Partial updates + Auto-calc)
```
MO: WH/MO/00003 dengan komponennya:
- Pollard Angsa (silo101)
- Kopra mesh (silo102)
- PKE Pellet (silo103)
- Mineral (tidak ada equipment, auto-calc from BoM)

Timeline:
08:00 - Middleware update silo101 & silo102
  POST /api/scada/mo/update-with-consumptions
  {
    "mo_id": "WH/MO/00003",
    "silo101": 1050,
    "silo102": 480
  }
  → quantity_done[silo101] = 1050
  → quantity_done[silo102] = 480
  → quantity_done[silo103] = 0 (no update)
  → Mineral = 0 (no equipment)

05:00 - Mark MO as done dengan auto_consume=true (smart mode)
  POST /api/scada/mo/mark-done
  {
    "mo_id": "WH/MO/00003",
    "finished_qty": 20000,
    "auto_consume": true
  }
  → System check:
    - silo101 (1050 > 0) → skip ✓ (keep middleware data)
    - silo102 (480 > 0) → skip ✓ (keep middleware data)
    - silo103 (0 = 0) → auto-calc from BoM ✓
    - Mineral (0 = 0) → auto-calc from BoM ✓

Result:
  - silo101: 1050 (from middleware)
  - silo102: 480 (from middleware)
  - silo103: 124.80 (auto-calc)
  - Mineral: 35.10 (auto-calc)
```

## State Check

Untuk MO yang belum di-mark done, consumption update bisa dilakukan pada state:
- ✅ `draft`
- ✅ `confirmed`
- ✅ `planned`
- ✅ `progress`

Untuk MO yang sudah:
- ❌ `done` - Error: Cannot update consumption
- ❌ `cancel` - Error: Cannot update consumption

## Implementation Files

### Modified/Added:

1. **grt_scada/services/middleware_service.py**
   - Modified: `apply_material_consumption()` - add update_mode parameter & state check
   - Modified: `_apply_consumption_to_moves()` - ADD mode logic
   - Added: `_apply_consumption_to_moves_replace()` - REPLACE mode logic

2. **grt_scada/controllers/main.py**
   - Updated: docstring untuk endpoint `/api/scada/material-consumption`

## API Response Codes

| Status | Message | MO State |
|--------|---------|----------|
| success↑ | Material consumption added | !done, !cancel |
| success↑ | Material consumption replaced | !done, !cancel |
| error❌ | Cannot update consumption for MO in done state | done |
| error❌ | Cannot update consumption for MO in cancel state | cancel |
| error❌ | MO not found | - |
| error❌ | No raw material move found | - |

## Best Practices

1. **Use ADD mode ketika:**
   - Equipment mengirim incremental updates
   - Production progress tracking
   - Cumulative consumption monitoring

2. **Use REPLACE mode ketika:**
   - Equipment mengirim revised/corrected values
   - Measurement corrections
   - Need to update actual final value

3. **Recommended workflow untuk production:**
   ```
   1. Middleware send consumption updates (ADD atau REPLACE)
      - Update boleh multiple times
      - Mo state harus != 'done'
   
   2. Ketika production selesai:
      POST /api/scada/mo/mark-done dengan auto_consume=false (default)
      - Jangan override consumption dari middleware
      - Hanya auto-calc untuk material yang belum ada consumption
   ```

## Testing

```javascript
// Test case 1: ADD multiple times
POST /api/scada/material-consumption
{mo_id: "WH/MO/00003", product_id: 123, quantity: 100, update_mode: "add"}
// quantity_done = 100

POST /api/scada/material-consumption
{mo_id: "WH/MO/00003", product_id: 123, quantity: 50, update_mode: "add"}
// quantity_done = 150 ✓

// Test case 2: REPLACE multiple times
POST /api/scada/material-consumption
{mo_id: "WH/MO/00003", product_id: 124, quantity: 200, update_mode: "replace"}
// quantity_done = 200

POST /api/scada/material-consumption
{mo_id: "WH/MO/00003", product_id: 124, quantity: 180, update_mode: "replace"}
// quantity_done = 180 ✓ (not 380)

// Test case 3: MO sudah done - should error
POST /api/scada/material-consumption
{mo_id: "WH/MO/00001", product_id: 125, quantity: 100}
// Error: Cannot update consumption for MO in done state ✓

// Test case 4: can_update_again flag
POST /api/scada/mo/mark-done
{mo_id: "WH/MO/00003", finished_qty: 20000}

POST /api/scada/material-consumption
{mo_id: "WH/MO/00003", product_id: 123, quantity: 50}
// Error: Cannot update consumption for MO in done state ✓
// can_update_again = false (dalam response sebelumnya)
```

## Kesimpulan

✅ **Ya, consumption BISA di-update multiple times dari middleware**  
✅ **Hanya bisa untuk MO yang belum di-mark done**  
✅ **Support 2 modes: ADD (default) dan REPLACE**  
✅ **Smart auto-consume tidak override middleware data**  

Sekarang middleware bisa mengirim update consumption berkali-kali sesuai kebutuhan production! 🎉
