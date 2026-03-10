# Panduan Product Template ID untuk Manual Weighing - GRT SCADA

## Ringkasan

Untuk keperluan **manual weighing** atau **manual consumption** di modul **grt_scada**, Anda memerlukan:
- **`product_id`** (ID variant produk dari `product.product`)
- **`product_tmpl_id`** (ID template produk dari `product.template`)

Kedua ID ini sudah tersedia di API endpoint dan bisa dicek menggunakan script yang disediakan.

---

## Field yang Tersedia

### 1. API Endpoint: `/api/scada/products`

**Response format:**
```json
[
  {
    "product_id": 1,
    "product_name": "Raw Material A",
    "product_tmpl_id": 1,
    "product_category": "Raw",
    "product_type": "product"
  }
]
```

**Field explanation:**
- `product_id`: ID variant produk (product.product)
- `product_tmpl_id`: ID template produk (product.template)
- `product_name`: Nama produk
- `product_category`: Kategori produk
- `product_type`: Tipe produk (product/consu/service)

---

## Cara Check Product Template ID

Tersedia 2 script untuk checking:

### Script 1: `check_product_tmpl_id.py` (XML-RPC)
```bash
# Lihat semua produk
python check_product_tmpl_id.py

# Filter by kategori
python check_product_tmpl_id.py "Raw"
python check_product_tmpl_id.py "Finished"
```

### Script 2: `check_product_tmpl_id_api.py` (SCADA API)
```bash
# Lihat semua produk via SCADA API
python check_product_tmpl_id_api.py

# Filter by kategori via SCADA API
python check_product_tmpl_id_api.py "Raw"
```

**Output example:**
```
================================================================================
 CHECK PRODUCT TEMPLATE ID - GRTSCADA Manual Weighing
================================================================================

Total produk ditemukan: 10

ID       Tmpl ID    Nama Produk                              Kategori            
--------------------------------------------------------------------------------
101      50         Jagung Giling                            Raw Material        
102      50         Dedak Padi                               Raw Material        
103      51         Feed Mix A (25kg)                        Finished Goods      
...
```

---

## Cara Pakai untuk Manual Weighing/Consumption

### Metode 1: Direct Model Creation (Internal)

```python
# Buat manual consumption record
consumption = env['scada.material.consumption'].create({
    'equipment_id': 1,
    'material_id': 101,  # Gunakan product_id
    'quantity': 50.0,
    'source': 'manual',
    'timestamp': fields.Datetime.now(),
})
```

### Metode 2: Via API (Recommended)

Lihat dokumentasi di `API_SPEC.md` untuk endpoint manual consumption:

```bash
# POST /api/scada/mo/manual-consumption
curl -X POST http://localhost:8069/api/scada/mo/manual-consumption \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "mo_id": 10,
      "consumptions": [
        {
          "product_id": 101,
          "quantity": 50.0
        }
      ]
    }
  }'
```

**Atau gunakan `product_tmpl_id`:**
```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "mo_id": 10,
    "consumptions": [
      {
        "product_tmpl_id": 50,  // System akan ambil variant pertama
        "quantity": 50.0
      }
    ]
  }
}
```

---

## Perbedaan product_id vs product_tmpl_id

| Aspek | product_id | product_tmpl_id |
|-------|-----------|-----------------|
| Model | `product.product` | `product.template` |
| Level | Variant | Template |
| Relasi | Many-to-one ke template | One-to-many ke variant |
| Penggunaan | Untuk transaksi spesifik | Untuk BoM lookup |
| Manual consumption | ✅ Primary | ✅ Fallback (auto pick variant) |

---

## Model Terkait

### `scada.material.consumption`

**Fields:**
```python
material_id = fields.Many2one('product.product')  # Gunakan product_id
quantity = fields.Float()
equipment_id = fields.Many2one('scada.equipment')
manufacturing_order_id = fields.Many2one('mrp.production')
source = fields.Selection([
    ('manual', 'Manual Entry'),
    ('api', 'API/Middleware'),
    ('auto_bom', 'Auto from BoM'),
])
```

### Service yang Handle product_tmpl_id

File: `grt_scada/models/scada_material_consumption.py`

Fungsi `prepare_consumption_data_from_payload()` bisa handle:
- `product_id` (prioritas)
- `product_tmpl_id` (fallback, ambil variant pertama)

---

## Tips

1. **Untuk manual weighing**, lebih baik gunakan `product_id` (variant spesifik)
2. **Untuk BoM lookup**, gunakan `product_tmpl_id` karena BoM biasanya defined di template level
3. **Check product_tmpl_id** sebelum kirim request manual weighing
4. **Pastikan produk active** (`active = True`) sebelum digunakan

---

## Troubleshooting

### Error: "Product not found"
- Check apakah product_id/product_tmpl_id valid menggunakan script check
- Pastikan produk dalam status active

### Error: "Product Template has no variant"
- Terjadi jika kirim product_tmpl_id yang tidak punya variant
- Solusi: gunakan product_id langsung atau tambah variant di Odoo

### Data tidak muncul di API
- Pastikan sudah login/authenticate
- Check filter category_name (case-insensitive wildcard)
- Periksa parameter `active` (default: true)

---

## Referensi

- API Documentation: `grt_scada/API_SPEC.md`
- Product Service: `grt_scada/services/product_service.py`
- Material Consumption Model: `grt_scada/models/scada_material_consumption.py`
- Controller: `grt_scada/controllers/main.py`

---

**Dibuat:** 2026-03-10  
**Module:** grt_scada v14.0  
**Author:** PT Gagak Rimang Teknologi
