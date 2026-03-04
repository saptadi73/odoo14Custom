# Diagram: SCADA Equipment Propagation Flow

## Flow Diagram 1: Before Fix (Manual Process)

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ BILL OF MATERIALS (BoM)                                                 ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ Product A                                                               ┃
┃ ├─ Component 1 → SILO_01  ✓                                            ┃
┃ ├─ Component 2 → SILO_02  ✓                                            ┃
┃ └─ Component 3 → SILO_03  ✓                                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

─────────────────────────────────────────────────────────────────────────────

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ CREATE MANUFACTURING ORDER (MO) from BoM                                ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                         ┃
┃ MO Components (BEFORE FIX):                                             ┃
┃ ├─ Component 1 → [EMPTY] ❌ USER MUST INPUT MANUALLY                    ┃
┃ ├─ Component 2 → [EMPTY] ❌ USER MUST INPUT MANUALLY                    ┃
┃ └─ Component 3 → [EMPTY] ❌ USER MUST INPUT MANUALLY                    ┃
┃                                                                         ┃
┃ User manually fills:                                                    ┃
┃ ├─ Component 1 → SILO_01  (typing needed) ⚠️                            ┃
┃ ├─ Component 2 → SILO_02  (typing needed) ⚠️                            ┃
┃ └─ Component 3 → SILO_03  (typing needed) ⚠️                            ┃
┃                                                                         ┃
┃ ⚠️ PROBLEMS:                                                            ┃
┃  • Time consuming for large BoM                                         ┃
┃  • Human error risk (typo, wrong selection)                             ┃
┃  • Inconsistent with BoM                                                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## Flow Diagram 2: After Fix (Automatic Process)

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ BILL OF MATERIALS (BoM)                                                 ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ Product A                                                               ┃
┃ ├─ Component 1 → SILO_01  ✓                                            ┃
┃ ├─ Component 2 → SILO_02  ✓                                            ┃
┃ └─ Component 3 → SILO_03  ✓                                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                              │
                              │
                    [AUTOMATIC DATA COPY]
                        ▼ ▼ ▼ ▼ ▼
─────────────────────────────────────────────────────────────────────────────

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ CREATE MANUFACTURING ORDER (MO) from BoM                                ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                         ┃
┃ MO Components (AFTER FIX):                                              ┃
┃ ├─ Component 1 → SILO_01  ✓ AUTOMATIC                                   ┃
┃ ├─ Component 2 → SILO_02  ✓ AUTOMATIC                                   ┃
┃ └─ Component 3 → SILO_03  ✓ AUTOMATIC                                   ┃
┃                                                                         ┃
┃ ✅ BENEFITS:                                                            ┃
┃  • Zero manual input needed                                             ┃
┃  • Consistent with BoM (no mistakes)                                    ┃
┃  • Fast (instant auto-fill)                                             ┃
┃  • User can still override if needed                                    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## Process Flow: Detailed Sync Logic

```
                    ┌──────────────────────────────────┐
                    │ User Creates MO from BoM         │
                    └─────────────┬──────────────────────┘
                                  │
                                  ▼
                    ╔══════════════════════════════════╗
                    ║ MrpProduction.create() called    ║
                    ╚══════════════════┬═══════════════╝
                                      │
                ┌─────────────────────┴──────────────────────┐
                │                                            │
                ▼                                            ▼
    ┌─────────────────────────────┐      ┌──────────────────────────┐
    │ 1. Check bom_id in vals     │      │ Skip if scada_equipment  │
    │    Auto-fill MO             │      │    already in vals       │
    │    scada_equipment_id       │      │                          │
    └──────────┬──────────────────┘      └──────────────────────────┘
               │
               ▼
    ╔═════════════════════════════════════════════════════════════╗
    ║ Call super().create()                                       ║
    ║ → MO created + stock moves auto-generated by Odoo core      ║
    ╚════════════════════════┬══════════════════════════════════╝
                            │
                            ▼
    ╔═════════════════════════════════════════════════════════════╗
    ║ [SYNC POINT #1] Call _sync_scada_equipment_to_moves()      ║
    ║                                                              ║
    ║ For each move in mo.move_raw_ids:                           ║
    ║  ├─ If move.scada_equipment_id exists? → SKIP              ║
    ║  └─ Else if move.bom_line_id exists?                       ║
    ║      └─ Copy bom_line.scada_equipment_id → move            ║
    ╚════════════════════════┬══════════════════════════════════╝
                            │
                            ▼
                    ┌──────────────────┐
                    │ MO Created ✓     │
                    │ with Equipment   │
                    └──────────────────┘
                            │
                            ▼
                    ┌──────────────────────────────┐
                    │ User Confirms MO             │
                    └─────────────┬────────────────┘
                                  │
                    ╔═════════════════════════════════════════════╗
                    ║ [SYNC POINT #2] action_confirm() override   ║
                    ║                                             ║
                    ║ Call _sync_scada_equipment_to_moves()       ║
                    ║ → Double-check all equipment is there       ║
                    ╚════════════════════┬═══════════════════════╝
                                        │
                                        ▼
                                ┌──────────────────┐
                                │ MO Confirmed ✓   │
                                │ Production Ready │
                                └──────────────────┘
```

---

## Technical Architecture

### Stock Move Creation Path

```
StockMove.create()
├─ For each vals in vals_list:
│  └─ If scada_equipment_id already present → SKIP
│     Else:
│     ├─ Check if bom_line_id in vals
│     │  └─ YES → Fetch bom_line.scada_equipment_id
│     │  └─ NO → Check if raw_material_production_id present
│     │            ├─ YES → Find matching BoM line via product_id
│     │            │        └─ Copy equipment from matching line
│     │            └─ NO → Leave empty
│     │
│     └─ Write scada_equipment_id to vals
│
└─ Call super().create() → Stock moves created with equipment
```

### MrpProduction Enhancement

```
MrpProduction.create()
├─ Auto-fill MO.scada_equipment_id from BoM if not provided
├─ Call super().create() → Creates MO + auto-generates stock moves
└─ [NEW] Call _sync_scada_equipment_to_moves()
    └─ Ensures all raw_material moves have equipment from BoM lines

MrpProduction.action_confirm()
├─ Call super().action_confirm() → Perform confirm logic
└─ [NEW] Call _sync_scada_equipment_to_moves()
    └─ Final verification/sync before production
```

---

## Error Prevention & Constraint

```
┌─────────────────────────────────────────────────────────────┐
│ Constraint: _check_unique_silo_equipment_per_mo             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Rule: One equipment can ONLY map to ONE material in MO      │
│                                                             │
│ Example VALID:          Example INVALID:                   │
│ • SILO_01 → Material A  • SILO_01 → Material A             │
│ • SILO_02 → Material B  • SILO_01 → Material B ❌ ERROR     │
│ • SILO_03 → Material C                                      │
│                                                             │
│ This prevents accidental mis-mapping where one equipment    │
│ is assigned to consume multiple different materials.        │
│                                                             │
│ Error Message:                                              │
│ "Equipment 'SILO_01' pada MO 'MO-001' sudah dipakai oleh   │
│  material 'Material A'. Satu equipment hanya boleh untuk    │
│  satu bahan."                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Multi-Scenario Testing Matrix

```
╔════════════════════════════════════════════════════════════════════════════╗
║ Scenario                              │ Expected Result                    ║
╠════════════════════════════════════════════════════════════════════════════╣
║ 1. BoM with SCADA setup, MO created  │ ✓ Equipment auto-filled in MO     ║
║    Qty = 1                           │                                    ║
╟────────────────────────────────────────────────────────────────────────────╢
║ 2. BoM with SCADA setup, MO created  │ ✓ Equipment auto-filled, scaling  ║
║    Qty > 1                           │   applied to component qty        ║
╟────────────────────────────────────────────────────────────────────────────╢
║ 3. BoM without SCADA setup            │ ✓ MO created, equipment empty    ║
║                                       │   (user can add if needed)        ║
╟────────────────────────────────────────────────────────────────────────────╢
║ 4. BoM partial SCADA setup            │ ✓ Only components with equipment  ║
║    (some lines with, some without)    │   in BoM get it in MO            ║
╟────────────────────────────────────────────────────────────────────────────╢
║ 5. User override equipment in MO      │ ✓ Manual value respected, not     ║
║    before confirm                     │   overwritten by sync            ║
╟────────────────────────────────────────────────────────────────────────────╢
║ 6. Duplicate equipment for 2          │ ✗ Constraint error thrown at      ║
║    different materials in MO          │   confirm/save                    ║
╟────────────────────────────────────────────────────────────────────────────╢
║ 7. MO with by-products                │ ✓ Only raw materials sync, by-    ║
║                                       │   products not affected           ║
╚════════════════════════════════════════════════════════════════════════════╝
```

---

## Timeline: When Sync Happens

```
                    Timeline of MO Lifecycle
                    
    07:00  ┌─────────────────────────────────┐
           │ 1. User enters form              │
           │ - Select BoM                     │
           │ - Set Quantity                   │
           └─────────────────────────────────┘
                           │
    07:05  ┌───────────────▼────────────────────────────────┐
           │ 2. Click SAVE (Create MO)                      │
           │ → MrpProduction.create() triggered            │
           │ → Stock moves generated by Odoo core           │
           │ → [SYNC #1] _sync_equipment_to_moves()        │
           │            Equipment filled into moves         │
           └─────────────────────────────────────────────────┘
                           │
    07:06  ┌───────────────▼────────────────────────────────┐
           │ 3. MO Created & View Loaded                    │
           │ - User sees components with equipment          │
           │ - Can verify or manually override if needed     │
           └─────────────────────────────────────────────────┘
                           │
    07:10  ┌───────────────▼────────────────────────────────┐
           │ 4. Click CONFIRM (Confirm MO)                  │
           │ → action_confirm() triggered                   │
           │ → [SYNC #2] _sync_equipment_to_moves()        │
           │            Final verification/sync             │
           │ → Core confirm logic proceeds                  │
           └─────────────────────────────────────────────────┘
                           │
    07:11  ┌───────────────▼────────────────────────────────┐
           │ 5. MO Confirmed                                │
           │ - Ready for production                         │
           │ - All equipment mapping complete               │
           │ - SCADA can now consume materials by SI LO     │
           └─────────────────────────────────────────────────┘
```

---

Generated: 02 March 2026
Module: grt_scada v7.0.73
