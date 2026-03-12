# API Report Dashboard SCADA Vue.js (One-Page)

Dokumen ringkas untuk handoff tim frontend Vue.js.
Fokus: endpoint report, params minimum, output wajib, dan pola integrasi.

## Base URL

`/api/scada`

## Endpoint Report Inti

| Endpoint | Method | Params Minimum (`params`) | Output Wajib untuk Dashboard |
|---|---|---|---|
| `/today-reports` | `POST` JSON-RPC | `{ "date": "YYYY-MM-DD", "limit": 200 }` | `batch_status`, `total_production_today`, `oee_quality_today`, `batch_to_batch_deviation_chart.data[]` |
| `/periodic-report` | `POST` JSON-RPC | `{ "period": "this_month", "limit": 1000 }` | `metrics_total_production`, `metrics_total_mo`, `metrics_avg_oee_quality`, `chart_daily_target_vs_actual.data[]`, `chart_raw_material_consumption.data[]`, `table_silo_consumption_stock.data[]`, `table_daily_finished_goods.data[]` |
| `/oee-equipment-avg` | `POST` JSON-RPC | `{ "period": "this_month", "limit": 100, "offset": 0 }` | `data[].equipment`, `data[].avg_summary`, `data[].avg_consumption_detail`, `data[].oee_records_count` |
| `/oee-detail` | `POST` JSON-RPC | `{ "mo_id": "WH/MO/00001", "limit": 50, "offset": 0 }` | `data[].mo_id`, `data[].product_name`, `data[].yield_percent`, `data[].consumption_ratio`, `data[].lines[]` |
| `/kpi-product-report` | `POST` JSON-RPC | `{ "period": "this_month", "limit": 100, "offset": 0 }` | `summary.total_products`, `summary.total_oee_records`, `data[].product_name`, `data[].avg_kpi` |
| `/equipment-failure-report` | `POST` JSON-RPC | `{ "period": "this_month", "limit": 100, "offset": 0 }` | `summary.total_failures`, `summary.equipment_count`, `summary.by_equipment[]`, `data[]` |

## Endpoint Pendukung Filter

| Endpoint | Method | Fungsi |
|---|---|---|
| `/products` | `GET` / `POST` JSON-RPC | Dropdown produk |
| `/products-by-category` | `POST` JSON-RPC | Dropdown bahan baku per kategori |
| `/boms` | `GET` / `POST` JSON-RPC | Komposisi BoM |
| `/mo-list` | `GET` | Daftar MO per equipment/status |
| `/mo-list-confirmed` | `POST` JSON-RPC | Queue MO confirmed |
| `/mo-list-detailed` | `POST` JSON-RPC | Detail MO + komponen + consumption |

## Kontrak Request (POST Report)

```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {}
}
```

## Template Fetch Frontend

```javascript
async function callScadaReport(endpoint, params = {}) {
  const response = await fetch(`/api/scada/${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      jsonrpc: '2.0',
      method: 'call',
      params,
    }),
  });

  const payload = await response.json();
  if (!response.ok || payload?.status === 'error' || payload?.error) {
    throw new Error(payload?.message || payload?.error?.message || 'Request failed');
  }

  return payload;
}
```

## Checklist Integrasi Minimum

1. Selalu kirim `credentials: 'include'`.
2. Selalu cek `status` sebelum render data.
3. Prioritaskan `today-reports` dan `periodic-report` untuk chart utama.
4. Endpoint lain umumnya data mentah dan perlu mapping chart/table di frontend.

## Referensi Detail Lengkap

Lihat dokumen utama: `API_SPEC.md` (section API report & endpoint detail lengkap).
