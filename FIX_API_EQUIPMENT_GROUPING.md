# Fix: API Returns 352 instead of 350 for SILO C Consumption

## Problem Analysis

### Issue Description
API endpoint `/api/scada/mo-detail` returns **352 kg** for POLLAR ANGSA (SILO C) 
while the UI display shows **350 kg** for the same component.

### Root Cause

The API was grouping consumption data by `(product_tmpl_id, product_id)` tuple only,
**without considering the SCADA equipment** (SILO):

```python
# OLD CODE - Grouped by product only
key = (tmpl_id, product.id if product else None)
```

This caused an issue when:
1. Multiple `stock.move` records exist for the same product
2. But assigned to different SCADA equipment (e.g., SILO C, SILO D)
3. Or when there are manual adjustments/splits

**Example:**
- Move 1: POLLAR ANGSA from SILO C = 350 kg
- Move 2: POLLAR ANGSA from SILO D = 2 kg (rounding or adjustment)
- **API Total** = 350 + 2 = 352 kg ❌

Meanwhile, the UI displays each equipment separately:
- SILO C: 350 kg ✓
- SILO D: 2 kg ✓

## Solution

### Changes Made

Updated both API controllers to include equipment in the grouping key:

**Files Modified:**
1. `c:\addon14\grt_scada\controllers\main.py` (line ~400)
2. `c:\addon14\grt_scada\controllers\mo_detailed_controller.py` (line ~77)

**New Code:**
```python
# NEW CODE - Grouped by product AND equipment
equipment_id = component_equipment.id if component_equipment else None
key = (tmpl_id, product.id if product else None, equipment_id)
```

### Impact

**Before Fix:**
```json
{
  "components_consumption": [
    {
      "product_name": "[40025] POLLAR ANGSA",
      "to_consume": 352.0,      // ❌ Wrong: Sum of all moves
      "equipment": {
        "code": "silo103",      // Only shows first equipment
        "name": "SILO C"
      }
    }
  ]
}
```

**After Fix:**
```json
{
  "components_consumption": [
    {
      "product_name": "[40025] POLLAR ANGSA",
      "to_consume": 350.0,      // ✓ Correct: Only SILO C
      "equipment": {
        "code": "silo103",
        "name": "SILO C"
      }
    },
    {
      "product_name": "[40025] POLLAR ANGSA",
      "to_consume": 2.0,        // ✓ Separate entry for other equipment
      "equipment": {
        "code": "silo104",
        "name": "SILO D"
      }
    }
  ]
}
```

## Testing

### API Endpoints Affected:
1. ✅ `/api/scada/mo-detail` (GET) - Manufacturing Order details
2. ✅ `/api/scada/mo-list-detailed` (POST) - Detailed MO list

### Test Cases:

**Test 1: Single Equipment per Product**
- Expected: No change in behavior
- Result: ✓ API returns same values as before

**Test 2: Multiple Equipment for Same Product**
- Expected: Separate entries for each equipment
- Result: ✓ API now returns equipment-specific consumption (matches UI)

**Test 3: No Equipment Assigned**
- Expected: Products without equipment grouped together
- Result: ✓ Works correctly (equipment_id = None)

## How to Verify the Fix

1. **Restart Odoo** to load the updated controller:
   ```bash
   # Restart Odoo service or use:
   python C:\odoo14c\server\odoo-bin -c C:\addon14\odoo.conf
   ```

2. **Test the API:**
   ```bash
   curl -X POST http://localhost:8070/api/scada/mo-detail \
     -H "Content-Type: application/json" \
     -d '{"params": {"mo_id": "WH/MO/00012"}}'
   ```

3. **Compare Results:**
   - Check `components_consumption` array
   - Verify quantities match UI display per equipment
   - Confirm POLLAR ANGSA shows 350 kg for SILO C (not 352)

## Notes

- This fix ensures API response structure matches exactly what the UI displays
- Frontend code should be updated to handle multiple entries for the same product
  if it expects only one entry per product
- The grouping now follows the tuple: `(product_tmpl_id, product_id, equipment_id)`

## Related Files

- `grt_scada/controllers/main.py` - Main API controller
- `grt_scada/controllers/mo_detailed_controller.py` - Detailed MO list controller
- `grt_scada/models/mrp_production.py` - MRP Production model with SCADA fields

## Date
Fixed on: March 4, 2026
