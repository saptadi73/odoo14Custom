# Fix: SCADA Equipment Automatic Propagation to Manufacturing Order

## Masalah
Ketika membuat manufacturing order (MO) dari Bill of Materials (BoM), informasi **SCADA Equipment** (Silo/Equipment) yang sudah diatur di BoM line **tidak otomatis dipropagasi** ke komponen MO (stock moves). 

**Akibatnya**: Pengguna harus secara manual mengisi kembali SCADA Equipment untuk setiap material/komponen di MO.

## Root Cause Analysis

Masalah terjadi karena:

1. **Timing Issue**: Saat Odoo core membuat stock moves dari BoM (pada saat MO dikonfirmasi), data `bom_line_id` mungkin tidak langsung tersedia atau tidak selalu inclusion dalam `vals_list` pada waktu create method dipanggil.

2. **Incomplete Data Flow**: 
   - BoM line memiliki field `scada_equipment_id`
   - Stock move (komponen MO) juga memiliki field `scada_equipment_id`
   - Namun, sinkronisasi antara keduanya tidak terjadi otomatis pada semua kondisi

3. **Method Hooks**: 
   - Onchange method `_onchange_bom_line_id_scada_equipment()` hanya bekerja pada form interaction
   - Tidak dipicu saat moves dibuat secara programmatic via `_generate_moves()`

## Solusi yang Diimplementasikan

### 1. **Enhanced Stock Move Creation** 
   - File: `grt_scada/models/stock_move.py`
   - Method: `create()` di-upgrade dengan dual approach:
     - **Direct approach**: Jika `bom_line_id` tersedia dalam vals, ambil equipment langsung
     - **Fallback approach**: Jika tidak ada, cari matching BoM line berdasarkan `product_id` dari MO

### 2. **New Sync Method in MrpProduction**
   - File: `grt_scada/models/mrp_production.py`
   - Menambahkan `_sync_scada_equipment_to_moves()` method yang:
     - Iterasi semua raw material moves di MO
     - Untuk setiap move, cek apakah sudah memiliki `scada_equipment_id`
     - Jika belum, ambil dari `bom_line_id.scada_equipment_id`

### 3. **Two Sync Hooks**
   - **Hook 1 - After Create**: `_sync_scada_equipment_to_moves()` dipanggil setelah MO dibuat
   - **Hook 2 - After Confirm**: `action_confirm()` di-override untuk memastikan sinkronisasi terjadi saat MO dikonfirmasi (ketika moves benar-benar di-generate)

## Technical Implementation

### Enhanced Stock Move Create Method
```python
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if vals.get('scada_equipment_id'):
            continue
        
        bom_line_id = vals.get('bom_line_id')
        if bom_line_id:
            # Direct bom_line_id provided
            bom_line = self.env['mrp.bom.line'].browse(bom_line_id)
            if bom_line and bom_line.scada_equipment_id:
                vals['scada_equipment_id'] = bom_line.scada_equipment_id.id
        elif vals.get('raw_material_production_id'):
            # Try to find bom_line through production order and product_id
            mo_id = vals.get('raw_material_production_id')
            product_id = vals.get('product_id')
            if mo_id and product_id:
                mo = self.env['mrp.production'].browse(mo_id)
                if mo and mo.bom_id:
                    # Find matching BoM line
                    matching_bom_lines = mo.bom_id.bom_line_ids.filtered(
                        lambda bl: bl.product_id.id == product_id
                    )
                    if matching_bom_lines:
                        bom_line = matching_bom_lines[0]
                        if bom_line.scada_equipment_id:
                            vals['scada_equipment_id'] = bom_line.scada_equipment_id.id
    
    return super().create(vals_list)
```

### New Sync Method in MrpProduction
```python
def _sync_scada_equipment_to_moves(self):
    """Sync SCADA equipment from BoM lines to corresponding raw material moves"""
    for mo in self:
        if not mo.bom_id:
            continue
        
        # Update raw material moves that don't have scada_equipment_id yet
        for move in mo.move_raw_ids:
            if move.scada_equipment_id or not move.bom_line_id:
                continue
            
            # Ambil equipment dari BoM line
            if move.bom_line_id and move.bom_line_id.scada_equipment_id:
                move.scada_equipment_id = move.bom_line_id.scada_equipment_id

def action_confirm(self):
    """Override confirm to ensure SCADA equipment is synced to moves"""
    res = super().action_confirm()
    self._sync_scada_equipment_to_moves()
    return res
```

## Impact & Benefits

### Sebelum Fix
- ❌ User harus manual input SCADA Equipment untuk setiap komponen MO
- ❌ Data di BoM tidak otomatis tercopy
- ❌ Risk of human error saat memasukkan equipment untuk multiple komponen
- ❌ Time consuming untuk large BoM dengan banyak komponen

### Setelah Fix
- ✅ SCADA Equipment otomatis dipropagasi dari BoM ke MO components
- ✅ Sinkronisasi terjadi di 2 titik: saat create dan saat confirm
- ✅ Multiple fallback mechanisms memastikan equipment terambil
- ✅ User hanya perlu input SCADA Equipment di BoM level (tidak di tiap MO)
- ✅ Lebih cepat dan mengurangi human error

## Testing Checklist

1. ✅ Create BoM dengan SCADA Equipment di setiap line
2. ✅ Create Manufacturing Order dari BoM tersebut
3. ✅ Verify bahwa MO component lines (move_raw_ids) sudah memiliki SCADA Equipment dari BoM
4. ✅ Confirm MO dan verify equipment masih ada
5. ✅ Test dengan multiple components, multiple SILOs
6. ✅ Verify constraint `_check_unique_silo_equipment_per_mo` masih bekerja

## Files Modified

1. **grt_scada/models/mrp_production.py**
   - Enhanced `create()` method
   - New `_sync_scada_equipment_to_moves()` method
   - Override `action_confirm()` method

2. **grt_scada/models/stock_move.py**
   - Enhanced `create()` method dengan fallback logic

## Compatibility

- ✅ Backward compatible (tidak menghapus existing functionality)
- ✅ Tidak mengubah database structure
- ✅ Existing records tidak terpengaruh (sync only applies ke new/edited records)
- ✅ Works dengan single dan multi-product BoM
