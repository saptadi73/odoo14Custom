# SCADA Failure Report API Documentation

Dokumen ini ditujukan untuk tim frontend yang akan mengimplementasikan integrasi dengan Vue.js.

Catatan penting:

- Modul ini sekarang menyediakan endpoint input data dan endpoint report.
- Endpoint report sudah disiapkan untuk frontend Vue.js + ApexCharts.
- Response report diusahakan langsung berbentuk `categories` dan `series` agar minim transformasi di frontend.

## 1. Endpoint

### Create Failure Report

- Method: `POST`
- URL: `/api/scada/failure-report`
- Type route Odoo: `json`
- Auth: `user`
- Content expectation: request JSON berbasis JSON-RPC Odoo, atau payload object biasa yang diproses menjadi dict

## 2. Tujuan Endpoint

Endpoint ini dipakai untuk membuat 1 record failure report baru ke model `scada.failure.report`.

Record yang dibuat berisi:

- `equipment_code`
- `description`
- `date`

## 3. Payload Request

Field yang diterima:

| Field | Type | Required | Keterangan |
|---|---|---:|---|
| `equipment_code` | string | Ya | Kode equipment, dicocokkan ke `scada.equipment.equipment_code` |
| `description` | string | Ya | Deskripsi failure |
| `date` | string | Tidak | Tanggal kejadian |

## 4. Format `date` yang didukung

Backend menerima format berikut:

- `YYYY-MM-DD HH:MM:SS`
- `YYYY-MM-DDTHH:MM`
- kosong/null: otomatis diisi waktu server saat create

Contoh valid:

- `2026-03-07 08:30:00`
- `2026-03-07T08:30`

Contoh invalid:

- `07/03/2026 08:30`
- `2026/03/07`

## 5. Contoh Request

### JSON object sederhana

```json
{
  "equipment_code": "PLC01",
  "description": "Motor overload saat proses mixing",
  "date": "2026-03-07 08:30:00"
}
```

### JSON-RPC style yang umum di Odoo

```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "equipment_code": "PLC01",
    "description": "Motor overload saat proses mixing",
    "date": "2026-03-07T08:30"
  }
}
```

## 6. Response

### Success response

```json
{
  "status": "success",
  "message": "Failure report created",
  "data": {
    "id": 1,
    "equipment_code": "PLC01",
    "description": "Motor overload saat proses mixing",
    "date": "2026-03-07 08:30:00"
  }
}
```

Makna field response:

| Field | Type | Keterangan |
|---|---|---|
| `status` | string | `success` jika create berhasil |
| `message` | string | Pesan hasil proses |
| `data.id` | integer | ID record baru |
| `data.equipment_code` | string | Kode equipment yang berhasil disimpan |
| `data.description` | string | Deskripsi failure |
| `data.date` | string | Datetime hasil simpan |

### Error response

Contoh field wajib kosong:

```json
{
  "status": "error",
  "message": "equipment_code is required"
}
```

Contoh equipment tidak ditemukan:

```json
{
  "status": "error",
  "message": "Equipment with code \"PLC01\" not found"
}
```

Contoh format tanggal salah:

```json
{
  "status": "error",
  "message": "Invalid date format. Use YYYY-MM-DD HH:MM:SS or YYYY-MM-DDTHH:MM"
}
```

## 7. Validasi Backend

Backend melakukan validasi berikut:

1. `equipment_code` wajib ada.
2. `description` wajib ada.
3. `equipment_code` harus cocok dengan data `scada.equipment`.
4. `date` harus dalam format yang didukung.

## 8. Mapping ke Vue.js Form

Field form frontend yang direkomendasikan:

| Input UI | Value yang dikirim |
|---|---|
| Select Equipment | `equipment_code` |
| Textarea Description | `description` |
| Datetime picker | `date` |

Contoh state Vue:

```js
const form = reactive({
  equipment_code: '',
  description: '',
  date: '',
})
```

Contoh submit dengan `fetch`:

```js
async function submitFailureReport() {
  const response = await fetch('/api/scada/failure-report', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({
      jsonrpc: '2.0',
      method: 'call',
      params: {
        equipment_code: form.equipment_code,
        description: form.description,
        date: form.date || null,
      },
    }),
  })

  const result = await response.json()
  const payload = result.result || result

  if (payload.status !== 'success') {
    throw new Error(payload.message || 'Failed to create failure report')
  }

  return payload.data
}
```

## 9. Handling Response di Vue.js

Praktik yang disarankan:

1. Ambil `result.result` dulu jika response dibungkus JSON-RPC Odoo.
2. Cek `status`.
3. Jika `status === 'success'`, tampilkan notifikasi sukses dan reset form.
4. Jika `status === 'error'`, tampilkan pesan backend apa adanya.

Contoh:

```js
try {
  const saved = await submitFailureReport()
  console.log('saved', saved)
  // show success toast
  // reset form
} catch (error) {
  console.error(error.message)
  // show error toast
}
```

## 10. Endpoint Report untuk ApexCharts

Frontend dapat memakai endpoint berikut.

### 10.1 KPI Summary

- `GET /api/scada/failure-report/report/kpi`
- `POST /api/scada/failure-report/report/kpi`

Parameter optional:

| Param | Type | Keterangan |
|---|---|---|
| `equipment_code` | string | filter equipment tertentu |
| `date_from` | string | filter tanggal mulai |
| `date_to` | string | filter tanggal akhir |

Contoh response:

```json
{
  "status": "success",
  "data": {
    "filters": {
      "equipment_code": null,
      "date_from": "2026-03-01 00:00:00",
      "date_to": "2026-03-31 23:59:59"
    },
    "kpis": {
      "total_failures": 42,
      "unique_equipment": 6,
      "latest_failure_at": "2026-03-07 08:30:00",
      "top_equipment": {
        "equipment_code": "PLC01",
        "equipment_name": "Mixer PLC 01",
        "failure_count": 12
      }
    }
  }
}
```

Use case:

- Summary cards
- Header dashboard

### 10.2 Failure by Equipment

- `GET /api/scada/failure-report/report/by-equipment`
- `POST /api/scada/failure-report/report/by-equipment`

Parameter optional:

| Param | Type | Keterangan |
|---|---|---|
| `date_from` | string | filter tanggal mulai |
| `date_to` | string | filter tanggal akhir |
| `limit` | integer | top N equipment, default `10` |

Contoh response:

```json
{
  "status": "success",
  "data": {
    "filters": {
      "equipment_code": null,
      "date_from": "2026-03-01 00:00:00",
      "date_to": "2026-03-31 23:59:59",
      "limit": 10
    },
    "chart": {
      "type": "bar",
      "categories": ["PLC01", "PLC02", "PLC03"],
      "series": [
        {
          "name": "Failure Count",
          "data": [12, 7, 3]
        }
      ]
    },
    "rows": [
      {
        "equipment_id": 1,
        "equipment_code": "PLC01",
        "equipment_name": "Mixer PLC 01",
        "failure_count": 12
      }
    ]
  }
}
```

Use case:

- Perbandingan jumlah failure antar equipment
- Ranking equipment paling sering failure

### 10.3 Failure Timeline

- `GET /api/scada/failure-report/report/timeline`
- `POST /api/scada/failure-report/report/timeline`

Parameter optional:

| Param | Type | Keterangan |
|---|---|---|
| `equipment_code` | string | filter equipment tertentu |
| `date_from` | string | filter tanggal mulai |
| `date_to` | string | filter tanggal akhir |
| `interval` | string | `day` atau `month`, default `day` |

Contoh response:

```json
{
  "status": "success",
  "data": {
    "filters": {
      "equipment_code": null,
      "date_from": "2026-03-01 00:00:00",
      "date_to": "2026-03-31 23:59:59",
      "interval": "day"
    },
    "chart": {
      "type": "line",
      "categories": ["2026-03-01", "2026-03-02", "2026-03-03"],
      "series": [
        {
          "name": "Failure Count",
          "data": [2, 5, 1]
        }
      ]
    }
  }
}
```

Use case:

- Trend failure harian
- Trend failure bulanan
- Monitoring naik/turun kejadian failure

### 10.4 Recent Failure List

- `GET /api/scada/failure-report/report/recent`
- `POST /api/scada/failure-report/report/recent`

Parameter optional:

| Param | Type | Keterangan |
|---|---|---|
| `equipment_code` | string | filter equipment tertentu |
| `date_from` | string | filter tanggal mulai |
| `date_to` | string | filter tanggal akhir |
| `limit` | integer | default `20` |
| `offset` | integer | default `0` |

Contoh response:

```json
{
  "status": "success",
  "data": {
    "filters": {
      "equipment_code": null,
      "date_from": null,
      "date_to": null,
      "limit": 20,
      "offset": 0
    },
    "total": 120,
    "items": [
      {
        "id": 10,
        "equipment_id": 1,
        "equipment_code": "PLC01",
        "equipment_name": "Mixer PLC 01",
        "description": "Motor overload",
        "date": "2026-03-07 08:30:00"
      }
    ]
  }
}
```

Use case:

- Table di bawah chart
- Recent incidents panel
- Detail drilldown setelah klik chart

## 11. Rekomendasi Chart untuk ApexCharts

### 11.1 Failure by Equipment

Rekomendasi chart:

- `horizontal bar chart`

Alasan:

- Label equipment biasanya lebih mudah dibaca secara horizontal
- Cocok untuk ranking top equipment
- Mudah dibandingkan antar kategori

Konfigurasi ApexCharts yang cocok:

```js
const options = {
  chart: { type: 'bar' },
  plotOptions: {
    bar: {
      horizontal: true,
      borderRadius: 4,
    },
  },
  xaxis: {
    categories: response.data.chart.categories,
  },
}

const series = response.data.chart.series
```

### 11.2 Failure Timeline

Rekomendasi chart:

- `line chart`
- alternatif: `area chart`

Alasan:

- Cocok untuk membaca trend dari waktu ke waktu
- Mudah melihat lonjakan failure
- Cocok untuk interval `day` dan `month`

Jika ingin tampilan lebih dashboard-friendly:

- gunakan `area chart` untuk visual yang lebih penuh

### 11.3 Share Failure per Equipment

Jika ingin versi komposisi, endpoint `by-equipment` juga bisa dipakai untuk:

- `donut chart`

Syarat:

- Gunakan top 5 atau top 6 saja
- Jangan terlalu banyak kategori karena donut chart cepat sulit dibaca

Cocok untuk:

- proporsi kontribusi failure per equipment

### 11.4 KPI Cards

Bukan chart, tapi sangat direkomendasikan:

- `Total Failures`
- `Unique Equipment`
- `Latest Failure At`
- `Top Equipment`

Sumber data:

- endpoint `report/kpi`

## 12. Rekomendasi Layout Dashboard

Susunan dashboard yang saya rekomendasikan:

1. Row 1: KPI cards
2. Row 2 kiri: Failure by Equipment (horizontal bar)
3. Row 2 kanan: Failure Timeline (line/area)
4. Row 3: Recent Failure List (table)

Kalau butuh chart ketiga:

5. Tambahkan donut chart Top 5 Equipment Share

## 13. Contoh Alur Fetch Vue.js

### By Equipment

```js
async function fetchFailureByEquipment(filters = {}) {
  const response = await fetch('/api/scada/failure-report/report/by-equipment', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({
      jsonrpc: '2.0',
      method: 'call',
      params: filters,
    }),
  })

  const result = await response.json()
  return result.result || result
}
```

### Timeline

```js
async function fetchFailureTimeline(filters = {}) {
  const response = await fetch('/api/scada/failure-report/report/timeline', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({
      jsonrpc: '2.0',
      method: 'call',
      params: {
        interval: 'day',
        ...filters,
      },
    }),
  })

  const result = await response.json()
  return result.result || result
}
```

## 14. Ringkasan Singkat

- Endpoint create tetap dipakai untuk input form
- Endpoint report baru siap dipakai untuk dashboard Vue.js + ApexCharts
- Chart yang paling direkomendasikan:
  - horizontal bar untuk by equipment
  - line/area untuk timeline
  - donut hanya untuk top few categories
