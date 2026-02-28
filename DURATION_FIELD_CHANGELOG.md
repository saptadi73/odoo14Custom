# Equipment Failure Duration Field Addition

## Overview
Added `duration` field to SCADA equipment failure report untuk mencatat durasi failure dalam format hh:mm (manual input).

## Changes Made

### 1. Model Changes
**File**: `models/scada_equipment_failure.py`

- **Field `duration`**: Char field untuk menyimpan durasi dalam format hh:mm
  - Format: `HH:MM` (e.g., 02:30 untuk 2 jam 30 menit)
  - Optional field - durasi bisa diisi manual sesuai kebutuhan
  - Validation dilakukan via `@api.constrains('duration')` - memastikan format yang valid

- **Computed Field `duration_minutes`**: Integer field yang computed dari `duration`
  - Otomatis convert format hh:mm ke total menit (e.g., 02:30 = 150 menit)
  - Useful untuk reporting dan analisis
  - Store=True untuk quick access di report

### 2. View Changes
**File**: `views/scada_equipment_failure_view.xml`

**Tree View (List)**: Tambahan kolom `duration` untuk menampilkan durasi failure

**Form View**: 
- Tambahan field `duration` dengan placeholder "HH:MM (e.g., 02:30)"
- Tambahan field `duration_minutes` (readonly) - untuk reference

### 3. API Controller Changes
**File**: `controllers/main.py`

Update 3 endpoints:

#### POST /api/scada/equipment-failure (Create)
- Accept parameter `duration` dari request body
- Return `duration` dan `duration_minutes` di response

#### GET /api/scada/equipment-failure (Get List)
- Adding `duration` dan `duration_minutes` fields ke response data

#### POST /api/scada/equipment-failure-report (Get Report)
- Adding `duration` dan `duration_minutes` fields ke response data

### 4. Database Migration
**File**: `migrations/7.0.59/pre-migration.py`

SQL migration untuk menambahkan kolom `duration` ke table `scada_equipment_failure`.

### 5. API Documentation
**File**: `API_SPEC.md`

Update dokumentasi untuk 3 endpoint equipment failure:
- **Section 19A**: Create Equipment Failure Report
- **Section 19B**: Get Equipment Failure Reports  
- **Section 19E**: Get Equipment Failure Report (Frontend)
- **Section 24**: Create Failure Report (Extension Module)

Menambahkan contoh request/response dengan field `duration` dan `duration_minutes`.

## Input Format

Duration field mengikuti format hh:mm:
- Valid: `00:00`, `01:30`, `12:45`, `23:59`
- Invalid: `24:00`, `12`, `12:60`, `invalid`

## Validation Rules

1. Format harus `HH:MM` (00-23 untuk jam, 00-59 untuk menit)
2. Validation dilakukan via `@api.constrains` decorator
3. Jika format invalid, sistem akan raise ValueError dengan pesan yang jelas

## Usage Examples

### Via UI Form
1. Buka Equipment Failure Report form
2. Isi field "Duration (hh:mm)" dengan format e.g., `02:30`
3. Field "Duration (minutes)" akan otomatis ter-compute dan ter-display (readonly)

### Via API (REST)
```bash
curl -X POST http://localhost:8069/api/scada/equipment-failure \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "equipment_code": "PLC01",
    "description": "Motor overload",
    "date": "2026-02-15 08:30:00",
    "duration": "02:30"
  }'
```

### Via API (JSON-RPC)
```bash
curl -X POST http://localhost:8069/api/scada/equipment-failure \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "equipment_code": "PLC01",
      "description": "Motor overload",
      "date": "2026-02-15 08:30:00",
      "duration": "02:30"
    }
  }'
```

## Response Format

```json
{
  "status": "success",
  "message": "Equipment failure report created",
  "data": {
    "id": 1,
    "equipment_code": "PLC01",
    "equipment_name": "Main PLC - Injection Machine 01",
    "description": "Motor overload",
    "date": "2026-02-15T08:30:00",
    "duration": "02:30",
    "duration_minutes": 150
  }
}
```

## Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `duration` | Char | No | Duration dalam format hh:mm (e.g., 02:30) |
| `duration_minutes` | Integer | No (Computed) | Duration converted to total minutes untuk reporting |

## Benefits

1. **Manual Input**: Durasi bisa diisi manual oleh operator, tidak hanya dari PLC
2. **Easy Tracking**: Mempermudah tracking berapa lama equipment down
3. **Auto Calculation**: `duration_minutes` otomatis ter-compute untuk analytics
4. **Format Validation**: Sistem validasi otomatis format hh:mm
5. **Report Ready**: Data siap untuk reporting dan analytics tanpa conversion

## Backward Compatibility

- Field adalah optional, tidak mandatory
- Data lama yang tidak punya duration akan tetap valid
- Existing API calls yang tidak mengirim `duration` tetap berfungsi normal
