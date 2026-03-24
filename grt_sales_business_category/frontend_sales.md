# Frontend Sales API

Dokumentasi ini disiapkan untuk frontend Vue.js yang akan terhubung ke modul `grt_sales_business_category`.

Fokus dokumen ini:

- login authentication via JSON-RPC
- penggunaan session Odoo dari frontend
- endpoint master data sales
- endpoint customer QR
- create draft Sales Order multi-item
- informasi accounting customer
- histori Sales Order customer

## Ringkasan Endpoint

| Endpoint | Method | Auth | Tujuan |
|---|---|---|---|
| `/api/sales/authenticate` | `POST` | public | login dan membuat session Odoo |
| `/api/sales/products` | `POST` | user | list product dan price |
| `/api/sales/payment-terms` | `POST` | user | list Term of Payment |
| `/api/sales/order-types` | `GET` | user | list type Sales Order |
| `/api/sales/customer-qr-by-id` | `POST` | user | ambil `customer_qr_ref` dari `customer_id` |
| `/api/sales/customer-qr-payload-by-id` | `POST` | user | ambil payload QR siap render dari `customer_id` |
| `/api/sales/customer-qr-payload-by-ref` | `POST` | user | ambil payload QR siap render dari `customer_qr_ref` |
| `/api/sales/customer-detail-by-qr` | `POST` | user | detail customer langsung dari `customer_qr_ref` |
| `/api/sales/customer-accounting-summary-by-qr` | `POST` | user | summary aging hutang/piutang dari `customer_qr_ref` |
| `/api/sales/orders-by-qr` | `POST` | user | histori Sales Order customer dari `customer_qr_ref` |
| `/api/sales/draft-order` | `POST` | user | create draft Sales Order multi-item |

## Base URL

Contoh base URL Odoo:

```text
https://your-odoo-host
```

Semua endpoint di bawah menggunakan base URL tersebut.

## Authentication Model

Frontend menggunakan session authentication bawaan Odoo.

Flow:

1. frontend memanggil endpoint login
2. Odoo mengembalikan `session_id`
3. browser atau client menyimpan cookie session
4. request berikutnya ke endpoint yang butuh login menggunakan session yang sama

Catatan:

- endpoint login bersifat `auth="public"`
- endpoint data sales berikutnya memakai `auth="user"`
- jika frontend berjalan beda domain, CORS dan cookie policy perlu disiapkan di server
- untuk aplikasi Vue.js, semua request session-based sebaiknya selalu memakai `credentials: "include"`

## JSON-RPC Request Format

Frontend dapat mengirim payload JSON-RPC sederhana dengan pola:

```json
{
  "params": {
    "key": "value"
  }
}
```

Controller saat ini juga menerima payload langsung tanpa wrapper `params`, tetapi disarankan tetap memakai `params` agar konsisten.

## Endpoint Login

### `POST /api/sales/authenticate`

Endpoint untuk login dari frontend Vue.js dan membuat session Odoo.

#### Request body

```json
{
  "params": {
    "login": "user@example.com",
    "password": "secret",
    "db": "database_name"
  }
}
```

#### Success response

```json
{
  "status": "success",
  "message": "Authentication successful",
  "data": {
    "uid": 12,
    "session_id": "2d2c7d9f....",
    "db": "database_name",
    "login": "user@example.com",
    "name": "Demo User",
    "partner_id": 45,
    "company_id": 1,
    "company_name": "PT Example"
  }
}
```

#### Error response

```json
{
  "status": "error",
  "message": "Invalid credentials"
}
```

## Customer QR Reference

Field `customer_qr_ref` tersedia di model `res.partner`.

Tujuan field ini:

- menjadi identifier unik customer untuk keperluan QR
- dipakai frontend untuk lookup customer
- bisa diminta dari backend berdasarkan `customer_id`
- bisa diambil dalam bentuk payload siap render untuk QR frontend
- bukan pengganti `partner_id`

Contoh format:

```text
CUSTQR2603-000001
```

Catatan implementasi:

- customer baru akan otomatis mendapat `customer_qr_ref`
- customer lama akan terisi saat module install atau upgrade
- referensi ini unik di database
- jika frontend sudah menyimpan `customer_qr_ref`, frontend tidak perlu lagi menampilkan atau mengirim `customer_id` untuk flow lookup customer
- flow yang sudah bisa langsung memakai `customer_qr_ref` adalah detail customer, summary accounting customer, dan histori order customer
- endpoint yang masih membutuhkan `customer_id` hanya endpoint pembangkit QR awal berbasis id: `customer-qr-by-id` dan `customer-qr-payload-by-id`
- frontend juga bisa membentuk ulang payload QR langsung dari reference melalui `customer-qr-payload-by-ref`

## Endpoint Master Data

### `POST /api/sales/products`

Mengambil list produk untuk kebutuhan form Sales Order.

#### Request body

```json
{
  "params": {
    "search": "",
    "limit": 50,
    "offset": 0
  }
}
```

#### Response

```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "product_id": 101,
        "default_code": "PRD-001",
        "name": "Produk A",
        "list_price": 12000.0,
        "uom_id": 1,
        "uom_name": "Unit",
        "currency_id": 13,
        "currency_name": "IDR"
      }
    ],
    "count": 1
  }
}
```

### `POST /api/sales/payment-terms`

Mengambil daftar Term of Payment.

#### Response

```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "payment_term_id": 1,
        "name": "Cash"
      },
      {
        "payment_term_id": 2,
        "name": "30 Days"
      }
    ]
  }
}
```

### `GET /api/sales/order-types`

Mengambil daftar type Sales Order dari backend.

#### Response

```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "value": "kering",
        "label": "Kering"
      },
      {
        "value": "basah",
        "label": "Basah"
      }
    ]
  }
}
```

## Panduan Frontend Jika Memakai `customer_qr_ref`

Jika sisi frontend sudah menyimpan `customer_qr_ref`, maka frontend bisa memakai reference tersebut sebagai identifier customer untuk flow setelah QR terbentuk atau setelah customer pernah dipilih sebelumnya.

Frontend bisa langsung memakai `customer_qr_ref` untuk endpoint berikut:

- `POST /api/sales/customer-detail-by-qr`
- `POST /api/sales/customer-accounting-summary-by-qr`
- `POST /api/sales/orders-by-qr`
- `POST /api/sales/customer-qr-payload-by-ref`

Contoh request umum:

```json
{
  "params": {
    "customer_qr_ref": "CUSTQR2603-000001"
  }
}
```

Catatan integrasi:

- jika frontend hanya perlu lookup ulang customer yang sudah punya QR reference, gunakan `customer_qr_ref`
- jika frontend ingin membuat atau membentuk ulang payload QR, frontend bisa memakai `customer_id` atau `customer_qr_ref` sesuai data yang tersedia
- `customer_qr_ref` sudah cukup untuk flow scan, detail customer, summary accounting, histori order, dan pembentukan ulang payload QR
## Endpoint Customer

### `POST /api/sales/customer-qr-by-id`

Mengambil `customer_qr_ref` dari `customer_id` untuk kebutuhan generate QR di frontend.

#### Request body

```json
{
  "params": {
    "customer_id": 45
  }
}
```

#### Response

```json
{
  "status": "success",
  "data": {
    "partner_id": 45,
    "customer_id": 45,
    "name": "PT Customer A",
    "customer_qr_ref": "CUSTQR2603-000001"
  }
}
```

### `POST /api/sales/customer-qr-payload-by-id`

Mengambil payload QR siap render dari `customer_id`.

Endpoint ini cocok jika frontend ingin langsung membuat QR tanpa menyusun data sendiri.

#### Request body

```json
{
  "params": {
    "customer_id": 45,
    "format": "ref"
  }
}
```

#### Field request

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `customer_id` | integer | ya | id customer / partner |
| `format` | string | tidak | `ref` atau `json`; default `ref` |

#### Response format `ref`

```json
{
  "status": "success",
  "data": {
    "partner_id": 45,
    "customer_id": 45,
    "name": "PT Customer A",
    "customer_qr_ref": "CUSTQR2603-000001",
    "format": "ref",
    "qr_content": "CUSTQR2603-000001",
    "qr_payload": {
      "customer_id": 45,
      "customer_qr_ref": "CUSTQR2603-000001",
      "customer_name": "PT Customer A"
    }
  }
}
```

#### Response format `json`

Request:

```json
{
  "params": {
    "customer_id": 45,
    "format": "json"
  }
}
```

Response:

```json
{
  "status": "success",
  "data": {
    "partner_id": 45,
    "customer_id": 45,
    "name": "PT Customer A",
    "customer_qr_ref": "CUSTQR2603-000001",
    "format": "json",
    "qr_content": "{\"customer_id\":45,\"customer_qr_ref\":\"CUSTQR2603-000001\",\"customer_name\":\"PT Customer A\"}",
    "qr_payload": {
      "customer_id": 45,
      "customer_qr_ref": "CUSTQR2603-000001",
      "customer_name": "PT Customer A"
    }
  }
}
```

Catatan:

- `qr_content` adalah isi yang langsung di-encode ke QR
- `format="ref"` cocok jika backend lookup nanti cukup pakai `customer_qr_ref`
- `format="json"` cocok jika frontend atau scanner ingin membaca metadata customer langsung dari isi QR
- `qr_payload` tetap selalu dikembalikan sebagai object referensi


### `POST /api/sales/customer-qr-payload-by-ref`

Mengambil payload QR siap render dari `customer_qr_ref`.

Endpoint ini cocok jika frontend sudah menyimpan reference customer dan ingin membentuk ulang payload QR tanpa membutuhkan `customer_id`.

#### Request body

```json
{
  "params": {
    "customer_qr_ref": "CUSTQR2603-000001",
    "format": "ref"
  }
}
```

#### Field request

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `customer_qr_ref` | string | ya | reference QR customer |
| `format` | string | tidak | `ref` atau `json`; default `ref` |

#### Response format `ref`

```json
{
  "status": "success",
  "data": {
    "partner_id": 45,
    "customer_id": 45,
    "name": "PT Customer A",
    "customer_qr_ref": "CUSTQR2603-000001",
    "format": "ref",
    "qr_content": "CUSTQR2603-000001",
    "qr_payload": {
      "customer_id": 45,
      "customer_qr_ref": "CUSTQR2603-000001",
      "customer_name": "PT Customer A"
    }
  }
}
```

#### Response format `json`

```json
{
  "status": "success",
  "data": {
    "partner_id": 45,
    "customer_id": 45,
    "name": "PT Customer A",
    "customer_qr_ref": "CUSTQR2603-000001",
    "format": "json",
    "qr_content": "{\"customer_id\":45,\"customer_qr_ref\":\"CUSTQR2603-000001\",\"customer_name\":\"PT Customer A\"}",
    "qr_payload": {
      "customer_id": 45,
      "customer_qr_ref": "CUSTQR2603-000001",
      "customer_name": "PT Customer A"
    }
  }
}
```
### `POST /api/sales/customer-detail-by-qr`

Mengambil detail customer berdasarkan `customer_qr_ref`.

#### Request body

```json
{
  "params": {
    "customer_qr_ref": "CUSTQR2603-000001"
  }
}
```

#### Response

```json
{
  "status": "success",
  "data": {
    "partner_id": 45,
    "name": "PT Customer A",
    "customer_qr_ref": "CUSTQR2603-000001",
    "street": "Jl. Contoh",
    "street2": null,
    "city": "Jakarta",
    "phone": "08123456789",
    "mobile": "08123456789",
    "email": "customer@example.com",
    "payment_term_id": 2,
    "payment_term_name": "30 Days"
  }
}
```

### `POST /api/sales/customer-accounting-summary-by-qr`

Mengambil nilai dan aging hutang/piutang customer berdasarkan `customer_qr_ref`.

#### Request body

```json
{
  "params": {
    "customer_qr_ref": "CUSTQR2603-000001"
  }
}
```

#### Response

```json
{
  "status": "success",
  "data": {
    "partner_id": 45,
    "customer_qr_ref": "CUSTQR2603-000001",
    "receivable_total": 15000000.0,
    "payable_total": 0.0,
    "currency": "IDR",
    "aging_receivable": {
      "current": 5000000.0,
      "1_30": 4000000.0,
      "31_60": 3000000.0,
      "61_90": 2000000.0,
      "over_90": 1000000.0
    },
    "aging_payable": {
      "current": 0.0,
      "1_30": 0.0,
      "31_60": 0.0,
      "61_90": 0.0,
      "over_90": 0.0
    }
  }
}
```

### `POST /api/sales/orders-by-qr`

Mengambil list Sales Order berdasarkan `customer_qr_ref`.

#### Request body

```json
{
  "params": {
    "customer_qr_ref": "CUSTQR2603-000001",
    "limit": 20,
    "offset": 0
  }
}
```

#### Response

```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "sale_order_id": 120,
        "name": "S000120",
        "date_order": "2026-03-14 09:30:00",
        "commitment_date": "2026-03-15 10:00:00",
        "amount_total": 3000000.0,
        "state": "sale",
        "approval_state": "approved",
        "sale_order_type": "kering"
      }
    ],
    "count": 1
  }
}
```

## Endpoint Create Draft Sales Order

### `POST /api/sales/draft-order`

Membuat draft Sales Order dari frontend dan mendukung multi-item.

#### Request body

Minimal kirim `partner_id` atau `customer_qr_ref`.

```json
{
  "params": {
    "partner_id": 45,
    "customer_qr_ref": "CUSTQR2603-000001",
    "commitment_date": "2026-03-15 10:00:00",
    "sale_order_type": "kering",
    "payment_term_id": 4,
    "team_id": 3,
    "business_category_id": 2,
    "note": "Kirim pagi",
    "order_line": [
      {
        "product_id": 1001,
        "product_uom_qty": 25,
        "price_unit": 12000
      },
      {
        "product_id": 1002,
        "product_uom_qty": 10,
        "price_unit": 18000
      },
      {
        "product_id": 1003,
        "product_uom_qty": 5
      }
    ]
  }
}
```

#### Struktur `order_line`

| Field | Type | Required | Keterangan |
|---|---|---|---|
| `product_id` | integer | ya | id produk |
| `product_uom_qty` | float | ya | quantity |
| `price_unit` | float | tidak | harga manual; jika kosong pakai harga product/pricelist |
| `name` | string | tidak | deskripsi item |

#### Response

```json
{
  "status": "success",
  "message": "Draft sales order created",
  "data": {
    "sale_order_id": 120,
    "name": "S000120",
    "state": "draft",
    "amount_total": 570000.0,
    "line_count": 3
  }
}
```

#### Validasi

- `partner_id` atau `customer_qr_ref` wajib ada
- jika keduanya dikirim, nilainya harus saling cocok
- `sale_order_type` hanya boleh `kering` atau `basah`
- `payment_term_id` harus valid
- `order_line` wajib minimal 1 item
- setiap line wajib punya `product_id` dan `product_uom_qty > 0`

## Urutan Integrasi Frontend

Urutan implementasi yang disarankan di Vue:

1. login ke `/api/sales/authenticate`
2. ambil master data: `products`, `payment-terms`, `order-types`
3. jika frontend punya `customer_id`, panggil `customer-qr-payload-by-id` untuk membentuk payload QR
4. jika frontend sudah punya `customer_qr_ref`, panggil `customer-qr-payload-by-ref`
5. pilih `format="ref"` jika QR hanya menyimpan reference string
6. pilih `format="json"` jika QR ingin menyimpan metadata customer di dalam kontennya
7. jika QR discan dan backend lookup memakai ref, panggil `customer-detail-by-qr`
8. panggil `customer-accounting-summary-by-qr`
9. panggil `orders-by-qr`
10. user pilih banyak item
11. submit ke `draft-order`
## Contoh Alur Request Lengkap

```javascript
await postJsonRpc(`${baseUrl}/api/sales/authenticate`, {
  login,
  password,
  db,
});

await postJsonRpc(`${baseUrl}/api/sales/products`, {
  search: "",
  limit: 50,
  offset: 0,
});

await postJsonRpc(`${baseUrl}/api/sales/payment-terms`, {});

await getJsonSession(`${baseUrl}/api/sales/order-types`);

await postJsonRpc(`${baseUrl}/api/sales/customer-qr-payload-by-id`, {
  customer_id: 45,
  format: "ref",
});


await postJsonRpc(`${baseUrl}/api/sales/customer-qr-payload-by-ref`, {
  customer_qr_ref,
  format: "ref",
});
await postJsonRpc(`${baseUrl}/api/sales/customer-detail-by-qr`, {
  customer_qr_ref,
});

await postJsonRpc(`${baseUrl}/api/sales/customer-accounting-summary-by-qr`, {
  customer_qr_ref,
});

await postJsonRpc(`${baseUrl}/api/sales/orders-by-qr`, {
  customer_qr_ref,
  limit: 20,
  offset: 0,
});

await postJsonRpc(`${baseUrl}/api/sales/draft-order`, payload);
```

## Standard Response

### Success

```json
{
  "status": "success",
  "message": "optional message",
  "data": {}
}
```

### Error

```json
{
  "status": "error",
  "message": "error message"
}
```

## Contoh Service Vue.js

```javascript
export async function postJsonRpc(url, params) {
  const response = await fetch(url, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ params }),
  });

  return response.json();
}

export async function getJsonSession(url) {
  const response = await fetch(url, {
    method: "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  });

  return response.json();
}
```

## Catatan Frontend Vue

- simpan data login user di Pinia atau store sejenis
- semua endpoint selain login harus dipanggil setelah session terbentuk
- handle session expired dengan redirect ke halaman login
- untuk list product dan order history, siapkan pagination
- form order sebaiknya memakai dynamic rows agar multi-item nyaman dipakai
- tampilkan warning jika `receivable_total` atau aging customer tinggi
- `customer-qr-by-id` cocok jika frontend hanya perlu string referensi QR
- `customer-qr-payload-by-id` cocok jika frontend ingin langsung render QR dan menyimpan metadata QR sekaligus dari `customer_id`
- `customer-qr-payload-by-ref` cocok jika frontend sudah menyimpan `customer_qr_ref` dan ingin membentuk ulang payload QR
- gunakan `format="ref"` jika flow scan tetap lookup ke backend dengan `customer_qr_ref`
- gunakan `format="json"` jika scanner/frontend perlu membaca detail dasar customer langsung dari isi QR

## Status Implementasi Saat Ini

Sudah tersedia:

- `POST /api/sales/authenticate`
- `POST /api/sales/products`
- `POST /api/sales/payment-terms`
- `GET /api/sales/order-types`
- `POST /api/sales/customer-qr-by-id`
- `POST /api/sales/customer-qr-payload-by-id`
- `POST /api/sales/customer-qr-payload-by-ref`
- `POST /api/sales/customer-detail-by-qr`
- `POST /api/sales/customer-accounting-summary-by-qr`
- `POST /api/sales/orders-by-qr`
- `POST /api/sales/draft-order`
- field `customer_qr_ref` di `res.partner`
- field `sale_order_type` di `sale.order`
- auto-generate `customer_qr_ref` untuk customer baru
- backfill `customer_qr_ref` untuk data existing saat install atau upgrade module

## Referensi File Backend

- endpoint sales: `grt_sales_business_category/controllers/main.py`
- customer QR ref: `grt_sales_business_category/models/res_partner.py`
- sales order model: `grt_sales_business_category/models/sale_order.py`
- accounting move model: `grt_sales_business_category/models/account_move.py`
- sequence QR ref: `grt_sales_business_category/data/res_partner_sequence.xml`
