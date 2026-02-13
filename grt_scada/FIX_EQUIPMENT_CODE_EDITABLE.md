# Fix: Equipment Code Sekarang Bisa Di-Edit

## Masalah
Field `equipment_code` di SCADA Equipment tidak bisa di-edit setelah record dibuat karena:
1. View memiliki `attrs="{'readonly': [('id', '!=', False)]}"` yang membuat field readonly saat record sudah punya ID
2. Field menggunakan `unique=True` yang terlalu strict

## Solusi

### 1. Update View (scada_equipment_view.xml)
- Hapus constraint `readonly` pada field `equipment_code`
- Sekarang field bisa di-edit kapan saja

**Sebelum:**
```xml
<field name="equipment_code" widget="text" attrs="{'readonly': [('id', '!=', False)]}"/>
```

**Sesudah:**
```xml
<field name="equipment_code" widget="text"/>
```

### 2. Update Model (scada_equipment.py)
- Hapus `unique=True` dari field definition
- Tambahkan custom constraint `_check_unique_equipment_code()` untuk validasi uniqueness

**Keuntungan approach ini:**
- **Lebih fleksibel**: Bisa di-edit tanpa perlu delete dan recreate
- **Lebih user-friendly**: Error message yang jelas jika ada duplikat
- **Tetap aman**: Constraint tetap memastikan tidak ada duplikasi
- **Better UX**: Bisa lihat error message sebelum save

## Perilaku Sebelum vs Sesudah

### Sebelum:
- ❌ Tidak bisa edit `equipment_code` setelah record dibuat
- ❌ Harus delete record dan buat ulang untuk ubah code

### Sesudah:
- ✅ Bisa edit `equipment_code` kapan saja
- ✅ Jika ada duplikat, akan muncul error message yang jelas
- ✅ Lebih efisien dan user-friendly

## Testing

```
1. Buka SCADA Equipment list
2. Klik salah satu equipment yang sudah exist
3. Klik Edit atau ubah equipment_code langsung
4. Perubahan seharusnya bisa di-save
5. Jika ada duplikat code, akan muncul error validation
```

## Perubahan File

### 1. `/grt_scada/views/scada_equipment_view.xml` (Line 38)
- Removed: `attrs="{'readonly': [('id', '!=', False)]}"`

### 2. `/grt_scada/models/scada_equipment.py`
- Removed: `unique=True` dari field definition (Line 24)
- Added: New constraint `_check_unique_equipment_code()` untuk custom validation (after line 168)

## Check List
- [x] Update view untuk remove readonly
- [x] Update model untuk remove unique=True
- [x] Add custom constraint untuk validasi
- [x] Test dapat di-edit
- [x] Test constraint prevention duplikat
