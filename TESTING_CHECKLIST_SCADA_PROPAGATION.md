# TESTING CHECKLIST: SCADA Equipment Auto-Propagation Fix

Date: 02 March 2026
Module: grt_scada v7.0.73
Status: Ready for Testing

---

## ✅ Pre-Testing Setup

- [ ] Code deployed to test environment
- [ ] Odoo service restarted
- [ ] Database backed up (safety first!)
- [ ] Test data set prepared
  - [ ] Multiple BoMs created
  - [ ] Various SCADA equipment assigned
  - [ ] Different quantities for testing

---

## 🧪 Test Case 1: Basic Functionality - Single Component MO

**Objective**: Verify SCADA equipment auto-fills for simple MO with 1 component

**Setup**:
```
BoM: TestProduct_001
├─ Material_A: qty = 10 → SILO_01
```

**Steps**:
1. [ ] Open BoM TestProduct_001
   - [ ] Verify Material_A has SILO_01 assigned
   - [ ] Save

2. [ ] Create new Manufacturing Order
   - [ ] Select TestProduct_001 as product
   - [ ] Select TestProduct_001 BoM
   - [ ] Set Quantity = 100
   - [ ] Click SAVE

3. [ ] Verify Component Section
   - [ ] Material_A row should show SILO_01 ✓
   - [ ] NO manual input was needed
   - [ ] Quantity auto-calculated as appropriate

**Expected Result**: ✅ PASS
- Component line shows SILO_01 automatically populated

**Actual Result**: 
- [ ] PASS 
- [ ] FAIL (describe issue):

**Screenshots**: 
- [ ] Before (BoM with equipment)
- [ ] After (MO with auto-filled equipment)

---

## 🧪 Test Case 2: Multi-Component MO

**Objective**: Verify SCADA equipment auto-fills for all components in a complex BoM

**Setup**:
```
BoM: ComplexProduct_001
├─ Material_A: qty = 10 → SILO_01
├─ Material_B: qty = 20 → SILO_02
├─ Material_C: qty = 5  → SILO_03
└─ Material_D: qty = 8  → SILO_01 (same as Material_A)
```

**Steps**:
1. [ ] Open BoM ComplexProduct_001
   - [ ] Verify all 4 materials have correct equipment assigned
   - [ ] Save

2. [ ] Create new Manufacturing Order
   - [ ] Select ComplexProduct_001
   - [ ] Set Quantity = 50
   - [ ] Click SAVE

3. [ ] Verify All Component Rows
   - [ ] Material_A → SILO_01 ✓
   - [ ] Material_B → SILO_02 ✓
   - [ ] Material_C → SILO_03 ✓
   - [ ] Material_D → SILO_01 ✓
   - [ ] All quantities correct and quantities auto-calculated

**Expected Result**: ✅ PASS
- All 4 components have correct SCADA equipment populated

**Actual Result**:
- [ ] PASS
- [ ] FAIL (describe issue):

**Screenshots**:
- [ ] MO component list with all equipment filled

---

## 🧪 Test Case 3: MO Quantity Scaling

**Objective**: Verify component quantities scale correctly when creating MO with different qty

**Setup**:
```
BoM: ScaledProduct
├─ Material_X: qty = 10 → SILO_A  (base unit = 1 unit of final product)
├─ Material_Y: qty = 5  → SILO_B
```

**Steps**:
1. [ ] Open BoM ScaledProduct (BASE: 1 unit final product)

2. [ ] Create MO with Qty = 100
   - [ ] SAVE
   - [ ] Check component quantities
     - [ ] Material_X should be 10 * 100 = 1000? OR...?
     - [ ] Material_Y should be 5 * 100 = 500? OR...?
     - [ ] Verify calculation (system scaling logic)
   - [ ] Check SCADA equipment
     - [ ] Material_X → SILO_A ✓
     - [ ] Material_Y → SILO_B ✓

3. [ ] Create another MO with Qty = 25
   - [ ] Verify quantities are correctly scaled
   - [ ] Verify equipment still auto-filled

**Expected Result**: ✅ PASS
- Quantities correctly scaled based on BoM base unit
- SCADA equipment populated even with different quantities

**Actual Result**:
- [ ] PASS
- [ ] FAIL (describe issue):

**Notes**: 
- Record actual scaling behavior observed
- Equipment population is priority (independent of qty)

---

## 🧪 Test Case 4: Confirm MO (Sync Point #2)

**Objective**: Verify SCADA equipment persists and syncs correctly when confirming MO

**Setup**: Use MO from Test Case 2

**Steps**:
1. [ ] Open previously created MO (ComplexProduct_001)

2. [ ] Before Confirm - Verify Equipment Present
   - [ ] Material_A → SILO_01 ✓
   - [ ] Material_B → SILO_02 ✓
   - [ ] Material_C → SILO_03 ✓
   - [ ] Material_D → SILO_01 ✓

3. [ ] Click CONFIRM button
   - [ ] Wait for confirmation process

4. [ ] After Confirm - Verify Equipment Persists
   - [ ] Material_A → SILO_01 ✓ (should NOT disappear!)
   - [ ] Material_B → SILO_02 ✓
   - [ ] Material_C → SILO_03 ✓
   - [ ] Material_D → SILO_01 ✓

5. [ ] Check stock.move records (backend)
   ```sql
   SELECT id, product_id, scada_equipment_id, state 
   FROM stock_move 
   WHERE raw_material_production_id = <MO_ID>
   ```
   - [ ] All raw_material moves should have scada_equipment_id populated
   - [ ] No NULL values in scada_equipment_id (for mapped materials)

**Expected Result**: ✅ PASS
- SCADA equipment survives confirm operation
- All stock moves have correct equipment assigned
- No data loss during confirm

**Actual Result**:
- [ ] PASS
- [ ] FAIL (describe issue):

**SQL Query Results**:
```
[Paste results here]
```

---

## 🧪 Test Case 5: Partial BoM (Some Components Without Equipment)

**Objective**: Verify system handles BoM where only SOME components have SCADA equipment

**Setup**:
```
BoM: MixedProduct
├─ Material_A: qty = 10 → SILO_X
├─ Material_B: qty = 20 → [EMPTY - No Equipment]
└─ Material_C: qty = 5  → SILO_Y
```

**Steps**:
1. [ ] Open BoM MixedProduct
   - [ ] Verify Material_A → SILO_X
   - [ ] Verify Material_B → [Empty] (intentional)
   - [ ] Verify Material_C → SILO_Y
   - [ ] Save

2. [ ] Create MO from this BoM
   - [ ] Qty = 50
   - [ ] Save

3. [ ] Verify Component Section
   - [ ] Material_A → SILO_X ✓ (auto-filled)
   - [ ] Material_B → [Empty] ✓ (correct, no equipment in BoM)
   - [ ] Material_C → SILO_Y ✓ (auto-filled)

**Expected Result**: ✅ PASS
- Only materials with BoM equipment get auto-filled
- Materials without BoM equipment remain empty (expected behavior)
- No errors thrown

**Actual Result**:
- [ ] PASS
- [ ] FAIL (describe issue):

---

## 🧪 Test Case 6: Manual Override

**Objective**: Verify user can still manually override equipment in MO if needed

**Setup**: Use MO from Test Case 1

**Steps**:
1. [ ] Open Created MO with Material_A → SILO_01

2. [ ] Manually Edit Component
   - [ ] In Material_A row, change SILO_01 → SILO_02 (different silo)
   - [ ] Save MO

3. [ ] Verify Change Persisted
   - [ ] Reload MO
   - [ ] Material_A should show SILO_02 (user override saved) ✓

4. [ ] Confirm MO
   - [ ] Click CONFIRM
   - [ ] Material_A should STILL show SILO_02 (not reverted to SILO_01)

**Expected Result**: ✅ PASS
- User manual override is respected
- System doesn't force BoM value over user choice
- Override persists through confirm

**Actual Result**:
- [ ] PASS
- [ ] FAIL (describe issue):

---

## 🧪 Test Case 7: Constraint Enforcement (Error Case)

**Objective**: Verify constraint prevents duplicate equipment mapping

**Setup**:
```
This is an ERROR SCENARIO - we're testing the ERROR is thrown correctly

BoM: InvalidProduct (intentionally bad setup)
├─ Material_A → SILO_SAME
├─ Material_B → SILO_SAME  (DUPLICATE - SHOULD CAUSE ERROR)
```

**Steps**:
1. [ ] Create BoM with above setup
   - [ ] Try to SAVE

2. [ ] Expected: CONSTRAINT ERROR should be thrown
   ```
   Error: Equipment 'SILO_SAME' sudah dipakai oleh material 'Material_A'. 
           Satu equipment hanya boleh untuk satu bahan.
   ```
   - [ ] [ ] Error is shown ✓

3. [ ] Correct the BoM by assigning different equipment to Material_B
   - [ ] Material_B → SILO_OTHER
   - [ ] Save BoM (should work now)

4. [ ] Create MO from corrected BoM - should work fine

**Expected Result**: ✅ PASS
- Constraint prevents invalid equipment mapping
- Clear error message shown to user
- Fix is straightforward

**Actual Result**:
- [ ] PASS (Constraint working)
- [ ] FAIL (describe issue):

---

## 🧪 Test Case 8: BoM with By-Products

**Objective**: Verify SCADA equipment sync only affects raw materials, not by-products

**Setup**:
```
BoM: ProductWithByProducts
├─ Material_A: qty = 10 → SILO_01  [Raw Material]
├─ Material_B: qty = 5  → SILO_02  [Raw Material]
└─ By-Product_X: qty = 3           [By-Product - NO equipment]
```

**Steps**:
1. [ ] Open BoM ProductWithByProducts
   - [ ] Set up as above
   - [ ] Verify By-Product_X has NO equipment assigned
   - [ ] Save

2. [ ] Create MO
   - [ ] Qty = 50
   - [ ] Save

3. [ ] Verify Components
   - [ ] Material_A → SILO_01 ✓ (raw material, auto-filled)
   - [ ] Material_B → SILO_02 ✓ (raw material, auto-filled)
   - [ ] By-Product_X → [Empty] ✓ (by-product, no equipment - correct)

4. [ ] Confirm MO
   - [ ] No issues should occur
   - [ ] By-products handled normally (system ignores them for SCADA)

**Expected Result**: ✅ PASS
- Raw materials get SCADA equipment
- By-products are unaffected (correct business logic)
- No errors

**Actual Result**:
- [ ] PASS
- [ ] FAIL (describe issue):

---

## 🧪 Test Case 9: Empty BoM (No SCADA Equipment at All)

**Objective**: Verify MO can still be created from BoM with NO SCADA equipment setup

**Setup**:
```
BoM: OldStyleProduct (created before SCADA module, no equipment)
├─ Material_A: qty = 10 → [Empty - No Equipment Field Set]
├─ Material_B: qty = 20 → [Empty]
```

**Steps**:
1. [ ] Open BoM OldStyleProduct
   - [ ] Verify NO equipment assigned to any material
   - [ ] Save

2. [ ] Create MO from this BoM
   - [ ] Qty = 100
   - [ ] Save

3. [ ] Verify Components
   - [ ] Material_A → [Empty] ✓ (no equipment in BoM, so empty in MO)
   - [ ] Material_B → [Empty] ✓

4. [ ] System should work normally
   - [ ] No errors about missing equipment
   - [ ] SCADA equipment is OPTIONAL, not required

**Expected Result**: ✅ PASS
- System doesn't break if SCADA equipment unused
- Backward compatibility maintained
- Users can still use system without SCADA mapping

**Actual Result**:
- [ ] PASS
- [ ] FAIL (describe issue):

---

## 📊 Performance Testing

### Test Case 10: Large BoM (50+ Components)

**Objective**: Verify performance is acceptable with large BoM

**Setup**: Create BoM with 50+ components, all with SCADA equipment

**Steps**:
1. [ ] Measure MO creation time
   - Start timer: ______
   - Create MO from large BoM
   - End timer: ______
   - Duration: ______ seconds

2. [ ] Measure MO confirm time
   - Start timer: ______
   - Click CONFIRM
   - End timer: ______
   - Duration: ______ seconds

**Performance Criteria**:
- [ ] MO creation < 5 seconds ✓
- [ ] Equipment sync < 1 second ✓
- [ ] MO confirm < 5 seconds ✓
- [ ] No timeouts
- [ ] No UI freezing

**Actual Result**:
- [ ] PASS (Performance acceptable)
- [ ] FAIL (describe performance issue):

---

## 🔧 Regression Testing

### Test Case 11: Existing MO Not Affected

**Objective**: Verify that MO created BEFORE the fix are not affected

**Setup**: 
- Have existing MO records created before this fix was deployed
- Some with manual equipment entries, some without

**Steps**:
1. [ ] Open pre-fix MO
   - [ ] Equipment should exactly as it was before
   - [ ] No unexpected changes

2. [ ] Try to edit and confirm pre-fix MO
   - [ ] Should work normally
   - [ ] No breaking changes

**Expected Result**: ✅ PASS
- Existing MO not modified
- No data migration needed
- Clean backward compatibility

**Actual Result**:
- [ ] PASS
- [ ] FAIL (describe issue):

---

## 📋 Summary Results

| Test Case | Status | Notes |
|-----------|--------|-------|
| 1. Basic 1-Component MO | [ ] PASS / [ ] FAIL | |
| 2. Multi-Component MO | [ ] PASS / [ ] FAIL | |
| 3. Quantity Scaling | [ ] PASS / [ ] FAIL | |
| 4. Confirm Sync | [ ] PASS / [ ] FAIL | |
| 5. Partial BoM | [ ] PASS / [ ] FAIL | |
| 6. Manual Override | [ ] PASS / [ ] FAIL | |
| 7. Constraint (Error) | [ ] PASS / [ ] FAIL | |
| 8. ByProducts | [ ] PASS / [ ] FAIL | |
| 9. Empty BoM | [ ] PASS / [ ] FAIL | |
| 10. Large BoM (50+) | [ ] PASS / [ ] FAIL | |
| 11. Regression (Pre-fix) | [ ] PASS / [ ] FAIL | |

### Overall Result: 
- [ ] ALL PASS - Ready for Production! ✅
- [ ] SOME FAIL - Needs adjustment before deploy ⚠️
- [ ] CRITICAL FAIL - Do not deploy ❌

---

## 📝 Issues Found & Action Items

| Issue # | Description | Severity | Action | Status |
|---------|-------------|----------|--------|--------|
| 1 | [Describe if any] | [ ] Critical / [ ] Major / [ ] Minor | [ ] Fix | [ ] Open |
| 2 | | | | |
| 3 | | | | |

---

## ✍️ Tester Information

**Name**: ___________________________
**Date**: ___________________________
**Environment**: Test / Staging / Production
**Odoo Version**: ___________________________
**Database**: ___________________________

**Testing Notes**:
```
[Additional notes, observations, or context]
```

---

## 📞 Sign-Off

- [ ] Tester: Confirms all tests passed and fix is ready
- [ ] QA Lead: Approves for production deployment
- [ ] Team Lead: Authorizes release

**Signatures**:
- Tester: _________________________ Date: _________
- QA Lead: ________________________ Date: _________
- Team Lead: ______________________ Date: _________

---

**Approval**: 
- [ ] ✅ APPROVED - Ready for Production Deployment
- [ ] ⚠️ CONDITIONAL - Approved with noted caveats below
- [ ] ❌ REJECTED - Do not deploy until resolved

Caveats/Notes:
```
[If conditional or rejected, explain here]
```
