# SCADA Middleware API Specification (Odoo 14)

**IMPLEMENTASI: JSON-RPC over HTTP**

Dokumentasi lengkap untuk JSON-RPC API endpoints yang compatible dengan Vue.js frontend.

## Base URL

```
http(s)://{odoo-host}/api/scada/
```

**Default**: `http://localhost:8069/api/scada/`

## Authentication

### For Vue.js Frontend (Browser-based)

Gunakan session-based authentication via cookies:

```bash
# 1. Login via Odoo session endpoint
curl -X POST http://localhost:8069/web/session/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "db": "your_database",
      "login": "admin@example.com",
      "password": "password"
    }
  }' \
  -c cookies.txt

# 2. Use session cookies untuk API calls
curl -X GET http://localhost:8069/api/scada/health \
  -b cookies.txt
```

### For Middleware/API Client

Gunakan endpoint autentikasi khusus middleware untuk mendapatkan session cookie:

```bash
# 1. Authenticate dan simpan cookie
curl -X POST http://localhost:8069/api/scada/authenticate \
  -H "Content-Type: application/json" \
  -d '{"db": "your_database", "login": "admin", "password": "admin"}' \
  -c cookies.txt

# 2. Use session cookies untuk API calls
curl -X POST http://localhost:8069/api/scada/material-consumption \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"equipment_id": "PLC01", "product_id": 123, "quantity": 10.5, ...}'
```

## Response Format

### Success Response

```json
{
  "status": "success",
  "message": "Description of successful operation",
  "data": { },
  "count": 10,
  "timestamp": "2025-02-06T10:30:00"
}
```

### Error Response

```json
{
  "status": "error",
  "message": "Human-readable error description"
}
```

---

## Endpoints Reference

### 1. Health Check (Public)

**Check SCADA Module Status**

```http
GET /api/scada/health
```

**Parameters**: None

**Response**:

```json
{
  "status": "ok",
  "message": "SCADA Module is running",
  "timestamp": "2025-02-06T10:30:00"
}
```

**cURL Example**:
```bash
curl -X GET http://localhost:8069/api/scada/health
```

---

### 2. Get Version (Public)

**Get SCADA Module Version**

```http
GET /api/scada/version
```

**Parameters**: None

**Response**:

```json
{
  "status": "success",
  "version": "1.0.0",
  "name": "SCADA for Odoo"
}
```

**cURL Example**:
```bash
curl -X GET http://localhost:8069/api/scada/version
```

---

### 3. Authenticate Session (Public)

**Create Session for Middleware**

```http
POST /api/scada/authenticate
Content-Type: application/json
```

**Request Body**:

```json
{
  "db": "your_database",
  "login": "admin",
  "password": "admin"
}
```

**Response**:

```json
{
  "status": "success",
  "uid": 1,
  "session_id": "<session_id>",
  "db": "your_database",
  "login": "admin"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8069/api/scada/authenticate \
  -H "Content-Type: application/json" \
  -d '{"db": "your_database", "login": "admin", "password": "admin"}' \
  -c cookies.txt
```

---

### 4. Create Material Consumption (Protected)

**Record Material Usage/Consumption**

```http
POST /api/scada/material-consumption
Auth: Session cookie
Content-Type: application/json
```

**Request Body** (gunakan `product_id` atau `material_id`):

```json
{
  "equipment_id": "PLC01",
  "product_id": 123,
  "quantity": 10.5,
  "timestamp": "2025-02-06T10:30:00",
  "mo_id": "MO/2025/001",
  "batch_number": "BATCH_001",
  "api_request_id": "REQ_12345"
}
```

**Response**:

```json
{
  "status": "success",
  "message": "Material consumption recorded successfully",
  "record_id": 123,
  "external_id": "123"
}
```

**Error Responses**:

```json
{
  "status": "error",
  "message": "Equipment not found: PLC01"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8069/api/scada/material-consumption \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "equipment_id": "PLC01",
    "product_id": 123,
    "quantity": 10.5,
    "timestamp": "2025-02-06T10:30:00"
  }'
```


### 5. Get Material Consumption (Protected)

**Retrieve Material Consumption Record**

```http
GET /api/scada/material-consumption/{record_id}
Auth: Session cookie
```

**Parameters**:
- `record_id` (path): Record ID to retrieve

**Response**:

```json
{
  "status": "success",
  "data": {
    "id": 123,
    "equipment_id": "PLC01",
    "product_id": 123,
    "quantity": 10.5,
    "timestamp": "2025-02-06T10:30:00",
    "status": "recorded",
    "sync_status": "pending"
  }
}
```

**cURL Example**:
```bash
curl -X GET http://localhost:8069/api/scada/material-consumption/123 \
  -b cookies.txt
```

---

### 6. Validate Material Consumption (Protected)

**Validate Material Consumption Data**

```http
POST /api/scada/material-consumption/validate
Auth: Session cookie
Content-Type: application/json
```

**Request Body**:

```json
{
  "equipment_id": "PLC01",
  "product_id": 123,
  "quantity": 10.5,
  "timestamp": "2025-02-06T10:30:00",
  "mo_id": "MO/2025/001"
}
```

**Response** (Valid):

```json
{
  "status": "success",
  "message": "Validation passed",
  "data": {
    "equipment_id": "PLC01",
    "product_id": 123,
    "quantity": 10.5,
    "timestamp": "2025-02-06T10:30:00"
  }
}
```

**Response** (Invalid):

```json
{
  "status": "error",
  "message": "Equipment not found: PLC01"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8069/api/scada/material-consumption/validate \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "equipment_id": "PLC01",
    "product_id": 123,
    "quantity": 10.5,
    "timestamp": "2025-02-06T10:30:00"
  }'
```

---

### 7. Get Manufacturing Order List (Protected)

**Retrieve Manufacturing Orders for Equipment**

```http
GET /api/scada/mo-list?equipment_id=PLC01&status=planned&limit=50&offset=0
Auth: Session cookie
```

**Parameters (JSON-RPC `params`)**:
- `equipment_id` (required): Equipment code
- `status` (optional): Filter by status ('planned', 'progress', 'done')
- `limit` (optional): Max records (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response**:

```json
{
  "status": "success",
  "message": "MO list retrieved successfully",
  "count": 10,
  "equipment_id": "PLC01",
  "data": [
    {
      "id": 1,
      "mo_id": "MO/2025/001",
      "product_id": "PROD001",
      "product_name": "Product Name",
      "quantity": 100.0,
      "status": "1",
      "status_text": "planned",
      "date_start": "2025-02-06T08:00:00",
      "date_end": "2025-02-06T16:00:00",
      "equipment_id": "PLC01",
      "created_at": "2025-02-06T07:50:00"
    }
  ]
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8069/api/scada/mo-list?equipment_id=PLC01&limit=50" \
  -b cookies.txt
```

---

### 8. Create MO Weight (Protected)

**Record actual weight and auto-calc target weight from BoM**

```http
POST /api/scada/mo-weight
Auth: Session cookie
Content-Type: application/json
```

**Request Body**:

```json
{
  "mo_id": "MO/2025/001",
  "weight_actual": 1200.5,
  "timestamp": "2025-02-06T10:30:00",
  "notes": "Weighing after production"
}
```

**Response**:

```json
{
  "status": "success",
  "message": "MO weight recorded successfully",
  "record_id": 10,
  "mo_id": "MO/2025/001",
  "target_weight": 1185.0,
  "weight_actual": 1200.5
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8069/api/scada/mo-weight \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "mo_id": "MO/2025/001",
    "weight_actual": 1200.5,
    "timestamp": "2025-02-06T10:30:00"
  }'
```

---

### 9. Get MO Weight (Protected)

**Retrieve MO weight records**

```http
GET /api/scada/mo-weight?mo_id=MO/2025/001&limit=50&offset=0
Auth: Session cookie
```

**Query Parameters**:
- `mo_id` (optional): MO name atau ID
- `limit` (optional): Max records (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response**:

```json
{
  "status": "success",
  "count": 1,
  "data": [
    {
      "id": 10,
      "mo_id": "MO/2025/001",
      "product_id": 123,
      "target_weight": 1185.0,
      "weight_actual": 1200.5,
      "timestamp": "2025-02-06T10:30:00",
      "notes": "Weighing after production"
    }
  ]
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8069/api/scada/mo-weight?mo_id=MO/2025/001" \
  -b cookies.txt
```

---

### 10. Acknowledge Manufacturing Order (Protected)

**Confirm Equipment Received MO Data**

```http
POST /api/scada/mo/{mo_id}/acknowledge
Auth: Session cookie
Content-Type: application/json
```

**Parameters**:
- `mo_id` (path): Manufacturing Order Data record ID

**Request Body**:

```json
{
  "equipment_id": "PLC01",
  "status": "acknowledged",
  "timestamp": "2025-02-06T08:00:00"
}
```

**Response**:

```json
{
  "status": "success",
  "message": "MO acknowledged successfully",
  "mo_id": 123
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8069/api/scada/mo/123/acknowledge \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "equipment_id": "PLC01",
    "status": "acknowledged",
    "timestamp": "2025-02-06T08:00:00"
  }'
```

---

### 11. Update Manufacturing Order Status (Protected)

**Update MO Production Status**

```http
POST /api/scada/mo/{mo_id}/update-status
Auth: Session cookie
Content-Type: application/json
```

**Parameters**:
- `mo_id` (path): Manufacturing Order Data record ID

**Request Body**:

```json
{
  "equipment_id": "PLC01",
  "status": "progress",
  "date_start_actual": "2025-02-06T08:00:00",
  "date_end_actual": "2025-02-06T16:00:00",
  "message": "Production started"
}
```

**Response**:

```json
{
  "status": "success",
  "message": "MO status updated successfully",
  "mo_id": 123
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8069/api/scada/mo/123/update-status \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "equipment_id": "PLC01",
    "status": "progress",
    "date_start_actual": "2025-02-06T08:00:00"
  }'
```

---

### 12. Mark Manufacturing Order Done (Protected)

**Complete Manufacturing Order**

```http
POST /api/scada/mo/{mo_id}/mark-done
Auth: Session cookie
Content-Type: application/json
```

**Parameters**:
- `mo_id` (path): Manufacturing Order Data record ID

**Request Body**:

```json
{
  "equipment_id": "PLC01",
  "date_end_actual": "2025-02-06T16:00:00",
  "message": "Production completed"
}
```

**Response**:

```json
{
  "status": "success",
  "message": "Manufacturing order marked as done",
  "mo_id": "MO/2025/001"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8069/api/scada/mo/123/mark-done \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "equipment_id": "PLC01",
    "date_end_actual": "2025-02-06T16:00:00"
  }'
```

---

### 13. Get Equipment Status (Protected)

**Retrieve Equipment Connection & Status**

```http
GET /api/scada/equipment/{equipment_code}
Auth: Session cookie
```

**Parameters**:
- `equipment_code` (path): Equipment code (e.g., PLC01)

**Response**:

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "equipment_code": "PLC01",
    "name": "PLC01",
    "connection_status": "connected",
    "is_active": true,
    "last_connected": "2025-02-06T10:30:00"
  }
}
```

**cURL Example**:
```bash
curl -X GET http://localhost:8069/api/scada/equipment/PLC01 \
  -b cookies.txt
```

---

### 14. Get Product List (Protected)

**Retrieve Product List**

```http
GET /api/scada/products?category_id=1&category_name=Raw&active=true&limit=100&offset=0
Auth: Session cookie
```

**JSON-RPC (POST)**:

```http
POST /api/scada/products
Auth: Session cookie
Content-Type: application/json
```

**JSON-RPC Body**:

```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "category_id": 1,
    "category_name": "Raw",
    "active": "true",
    "limit": 100,
    "offset": 0
  }
}
```

**Query Parameters**:
- `category_id` (optional): Product category ID
- `category_name` (optional): Product category name (ilike)
- `active` (optional): true | false | all (default: true)
- `limit` (optional): Max records (default: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response**:

```json
[
  {
    "product_id": 1,
    "product_name": "Raw Material A",
    "product_tmpl_id": 1,
    "product_category": "Raw",
    "product_type": "product"
  },
  {
    "product_id": 2,
    "product_name": "Raw Material B",
    "product_tmpl_id": 2,
    "product_category": "Raw",
    "product_type": "product"
  }
]
```

Note: `product_tmpl_id` is included to support BoM lookup (template-level BoM).

**cURL Example**:
```bash
curl -X GET "http://localhost:8069/api/scada/products?category_name=Raw&active=true" \
  -b cookies.txt
```

**JSON-RPC Example**:
```bash
curl -X POST http://localhost:8069/api/scada/products \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "limit": 100
    }
  }'
```

---

### 15. Get Product List by Category (Protected)

**Retrieve Product List with Category Filter (JSON-RPC)**

```http
POST /api/scada/products-by-category
Auth: Session cookie
Content-Type: application/json
```

**Query Parameters**:
- `category_id` (optional): Product category ID
- `category_name` (optional): Product category name (ilike)
- `active` (optional): true | false | all (default: true)
- `limit` (optional): Max records (default: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response**: Same as [Get Product List](#14-get-product-list-protected).

**JSON-RPC Example**:
```bash
curl -X POST http://localhost:8069/api/scada/products-by-category \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "category_name": "Raw",
      "limit": 100
    }
  }'
```

**Example Response**:
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

---

### 16. Get BoM List (Protected)

**Retrieve BoM list with components**

```http
GET /api/scada/boms?product_tmpl_id=123&limit=50&offset=0
Auth: Session cookie
```

**JSON-RPC (POST)**:

```http
POST /api/scada/boms
Auth: Session cookie
Content-Type: application/json
```

**Query Parameters**:
- `bom_id` (optional): BoM ID
- `product_tmpl_id` (optional): Product template ID (recommended for template-level BoM)
- `product_id` (optional): Product variant ID (will be mapped to template if possible)
- `active` (optional): true | false | all (default: true)
- `limit` (optional): Max records (default: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response**:

```json
[
  {
    "bom_id": 10,
    "bom_code": "BOM-0001",
    "product_tmpl_id": 5,
    "product_tmpl_name": "Feed Mix A",
    "product_id": 12,
    "product_name": "Feed Mix A (25kg)",
    "product_qty": 1.0,
    "uom": "Units",
    "type": "normal",
    "components": [
      {
        "product_id": 101,
        "product_name": "Jagung Giling",
        "quantity": 20.0,
        "uom": "kg"
      },
      {
        "product_id": 102,
        "product_name": "Bungkil Kedelai",
        "quantity": 5.0,
        "uom": "kg"
      }
    ]
  }
]
```

Note: `product_id` is only included when the BoM is specific to a product variant. For template-level BoM, use `product_tmpl_id`.

**cURL Example**:
```bash
curl -X GET "http://localhost:8069/api/scada/boms?product_id=123&limit=50" \
  -b cookies.txt
```

**JSON-RPC Example**:
```bash
curl -X POST http://localhost:8069/api/scada/boms \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "product_tmpl_id": 123,
      "limit": 50
    }
  }'
```

---

## Error Handling

### Common Error Codes & Messages

| HTTP Status | Message | Meaning |
|---|---|---|
| 400 | Equipment not found | Equipment code tidak valid |
| 400 | Product not found | Product ID tidak ada di sistem |
| 400 | Validation failed | Data tidak valid |
| 401 | Unauthorized | Session tidak valid atau expired |
| 404 | MO record not found | Record ID tidak valid |
| 500 | Server error | Error di backend |

### Example Error Response

```json
{
  "status": "error",
  "message": "Equipment not found: PLC99"
}
```

---

## Integration Examples

### JavaScript/Vue.js

```javascript
// Using fetch (session stored in cookies)
async function login() {
  const response = await fetch('http://localhost:8069/api/scada/authenticate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      db: 'your_database',
      login: 'admin',
      password: 'admin'
    }),
    credentials: 'include'
  });

  const result = await response.json();
  if (result.status === 'error') {
    throw new Error(result.message);
  }
}

async function createMaterialConsumption(data) {
  const response = await fetch(
    'http://localhost:8069/api/scada/material-consumption',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
      credentials: 'include'
    }
  );
  
  const result = await response.json();
  if (result.status === 'error') {
    throw new Error(result.message);
  }
  return result;
}

// Usage
try {
  await login();
  const result = await createMaterialConsumption({
    equipment_id: 'PLC01',
    product_id: 123,
    quantity: 10.5,
    timestamp: new Date().toISOString()
  });
  console.log('Record created:', result.record_id);
} catch (error) {
  console.error('Error:', error.message);
}
```

### Python

```python
import requests
from datetime import datetime

base_url = 'http://localhost:8069/api/scada'
session = requests.Session()

# Authenticate and store session cookie
auth_response = session.post(
  f'{base_url}/authenticate',
  json={
    'db': 'your_database',
    'login': 'admin',
    'password': 'admin'
  }
)
auth_result = auth_response.json()
if auth_result.get('status') == 'error':
  raise RuntimeError(auth_result.get('message'))

# Create material consumption
data = {
    'equipment_id': 'PLC01',
  'product_id': 123,
    'quantity': 10.5,
    'timestamp': datetime.now().isoformat()
}

response = session.post(f'{base_url}/material-consumption', json=data)

result = response.json()
if result['status'] == 'success':
    print(f"Created record: {result['record_id']}")
else:
    print(f"Error: {result['message']}")
```

### cURL

```bash
#!/bin/bash

BASE_URL="http://localhost:8069/api/scada"

# Authenticate and store session cookie
curl -X POST "${BASE_URL}/authenticate" \
  -H "Content-Type: application/json" \
  -d '{"db": "your_database", "login": "admin", "password": "admin"}' \
  -c cookies.txt

# Health check
curl -X GET "${BASE_URL}/health"

# Create material consumption
curl -X POST "${BASE_URL}/material-consumption" \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "equipment_id": "PLC01",
    "product_id": 123,
    "quantity": 10.5,
    "timestamp": "2025-02-06T10:30:00"
  }'

# Get MO list
curl -X GET "${BASE_URL}/mo-list?equipment_id=PLC01" \
  -b cookies.txt

# Mark MO done
curl -X POST "${BASE_URL}/mo/123/mark-done" \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"date_end_actual": "2025-02-06T16:00:00"}'
```

---

## Best Practices

1. **Always use HTTPS in production**
2. **Keep session cookies secure** - avoid exposing cookies in logs
3. **Handle errors gracefully** - check `status` field before accessing `data`
4. **Add request timeouts** - prevent hanging requests
5. **Validate data** - use the `/validate` endpoints before creating records
6. **Log API calls** - important untuk troubleshooting
7. **Rate limiting** - implement backoff for failed requests
8. **Async operations** - don't block UI on API calls

---

## Documentation

- **Vue.js Integration**: See [JSONRPC_VUEJS_GUIDE.md](JSONRPC_VUEJS_GUIDE.md)
- **Python Integration**: See [JSONRPC_VUEJS_GUIDE.md](JSONRPC_VUEJS_GUIDE.md) (Python examples section)
- **Troubleshooting**: See main [README.md](README.md)
