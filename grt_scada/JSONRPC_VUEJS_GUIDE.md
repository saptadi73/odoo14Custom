"""
SCADA JSON-RPC API Documentation
Complete guide untuk Vue.js Frontend Integration

Odoo 14 SCADA Module - JSON-RPC Endpoints
"""

# ============================================================================
# AUTHENTICATION
# ============================================================================

## Method 1: Using Session ID (Recommended for Vue/Browser)

```javascript
// 1. Login dan dapatkan token
async function login(username, password) {
  const response = await fetch('http://localhost:8069/web/session/authenticate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      method: 'call',
      params: {
        db: 'your_database',
        login: username,
        password: password
      }
    })
  });
  
  const data = await response.json();
  if (data.error) {
    throw new Error(data.error.data.message);
  }
  
  // Session ID sudah disimpan di cookies otomatis
  return data.result;
}

// 2. Use session untuk API calls (cookies akan otomatis dikirim)
async function apiCall(endpoint, method = 'GET', body = null) {
  const options = {
    method: method,
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include', // Penting! Kirim cookies
  };
  
  if (body) {
    options.body = JSON.stringify(body);
  }
  
  const response = await fetch(`http://localhost:8069/api/scada${endpoint}`, options);
  return response.json();
}
```

## Method 2: Using Bearer Token (untuk middleware/API client)

```javascript
// Dapatkan token dari Odoo ke middleware (one-time setup)
const token = '2'; // Session ID atau API token

// Gunakan bearer token di setiap request
async function apiCallWithToken(endpoint, method = 'GET', body = null, token) {
  const options = {
    method: method,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  };
  
  if (body) {
    options.body = JSON.stringify(body);
  }
  
  const response = await fetch(`http://localhost:8069/api/scada${endpoint}`, options);
  return response.json();
}
```

# ============================================================================
# VUE.JS INTEGRATION EXAMPLE
# ============================================================================

## Setup API Service (composable or Vuex)

```javascript
// composables/useScadaApi.js
import { ref } from 'vue';

export function useScadaApi() {
  const token = ref(localStorage.getItem('scada_token'));
  const apiBaseUrl = 'http://localhost:8069/api/scada';

  const setToken = (newToken) => {
    token.value = newToken;
    localStorage.setItem('scada_token', newToken);
  };

  const apiCall = async (endpoint, method = 'GET', body = null) => {
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token.value}`,
      },
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(`${apiBaseUrl}${endpoint}`, options);
    const data = await response.json();
    
    if (data.status === 'error') {
      throw new Error(data.message);
    }
    
    return data;
  };

  return {
    token,
    setToken,
    apiCall,
  };
}
```

## Vue Component Example

```vue
<template>
  <div class="scada-dashboard">
    <!-- Health Check -->
    <div class="card">
      <h3>System Status</h3>
      <p v-if="systemStatus">{{ systemStatus.message }}</p>
      <button @click="checkHealth">Check Health</button>
    </div>

    <!-- Material Consumption Form -->
    <div class="card">
      <h3>Record Material Consumption</h3>
      <form @submit.prevent="createMaterialConsumption">
        <input v-model="consumption.equipment_id" placeholder="Equipment ID" required />
        <input v-model="consumption.material_code" placeholder="Material Code" required />
        <input v-model.number="consumption.quantity" type="number" placeholder="Quantity" required />
        <input v-model="consumption.timestamp" type="datetime-local" required />
        <button type="submit">Save</button>
      </form>
      <p v-if="consumptionResult" :class="consumptionResult.status">
        {{ consumptionResult.message }}
      </p>
    </div>

    <!-- MO List -->
    <div class="card">
      <h3>Manufacturing Orders</h3>
      <select v-model="equipmentFilter">
        <option value="">Select Equipment</option>
        <option>PLC01</option>
        <option>PLC02</option>
      </select>
      <button @click="fetchMOList">Load MOs</button>
      <table v-if="moList.length">
        <thead>
          <tr>
            <th>MO ID</th>
            <th>Product</th>
            <th>Qty</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="mo in moList" :key="mo.id">
            <td>{{ mo.mo_id }}</td>
            <td>{{ mo.product_name }}</td>
            <td>{{ mo.quantity }}</td>
            <td>{{ mo.status_text }}</td>
            <td>
              <button @click="acknowledgeMO(mo.id)">Ack</button>
              <button @click="markMODone(mo.id)">Done</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useScadaApi } from '@/composables/useScadaApi';

const { apiCall } = useScadaApi();

const systemStatus = ref(null);
const consumption = reactive({
  equipment_id: '',
  material_code: '',
  quantity: 0,
  timestamp: new Date().toISOString().slice(0, 16),
});
const consumptionResult = ref(null);
const equipmentFilter = ref('');
const moList = ref([]);

const checkHealth = async () => {
  try {
    systemStatus.value = await apiCall('/health');
  } catch (error) {
    console.error('Health check failed:', error);
  }
};

const createMaterialConsumption = async () => {
  try {
    consumptionResult.value = await apiCall('/material-consumption', 'POST', consumption);
    if (consumptionResult.value.status === 'success') {
      Object.assign(consumption, {
        equipment_id: '',
        material_code: '',
        quantity: 0,
      });
    }
  } catch (error) {
    consumptionResult.value = { status: 'error', message: error.message };
  }
};

const fetchMOList = async () => {
  try {
    const params = new URLSearchParams({
      equipment_id: equipmentFilter.value,
      limit: 50,
    });
    const result = await apiCall(`/mo-list?${params}`);
    moList.value = result.data || [];
  } catch (error) {
    console.error('Failed to fetch MO list:', error);
  }
};

const acknowledgeMO = async (moId) => {
  try {
    await apiCall(`/mo/${moId}/acknowledge`, 'POST', {});
    alert('MO acknowledged');
  } catch (error) {
    alert('Error: ' + error.message);
  }
};

const markMODone = async (moId) => {
  try {
    await apiCall(`/mo/${moId}/mark-done`, 'POST', {});
    alert('MO marked as done');
    await fetchMOList();
  } catch (error) {
    alert('Error: ' + error.message);
  }
};

onMounted(() => {
  checkHealth();
});
</script>
```

# ============================================================================
# ENDPOINTS REFERENCE
# ============================================================================

## 1. Health Check (Public)
```
GET /api/scada/health

Response:
{
  "status": "ok",
  "message": "SCADA Module is running",
  "timestamp": "2025-02-06T10:30:00"
}
```

## 2. Get Version (Public)
```
GET /api/scada/version

Response:
{
  "status": "success",
  "version": "1.0.0",
  "name": "SCADA for Odoo"
}
```

## 3. Create Material Consumption (Protected)
```
POST /api/scada/material-consumption
Authorization: Bearer {token}
Content-Type: application/json

Body:
{
  "equipment_id": "PLC01",
  "material_code": "MAT001",
  "quantity": 10.5,
  "timestamp": "2025-02-06T10:30:00",
  "batch_number": "BATCH_001"
}

Response:
{
  "status": "success",
  "message": "Material consumption recorded successfully",
  "record_id": 123,
  "external_id": "123"
}
```

## 4. Get Material Consumption (Protected)
```
GET /api/scada/material-consumption/123
Authorization: Bearer {token}

Response:
{
  "status": "success",
  "data": {
    "id": 123,
    "equipment_id": "PLC01",
    "material_code": "MAT001",
    "quantity": 10.5,
    "timestamp": "2025-02-06T10:30:00",
    "status": "recorded"
  }
}
```

## 5. Validate Material Consumption (Protected)
```
POST /api/scada/material-consumption/validate
Authorization: Bearer {token}
Content-Type: application/json

Body:
{
  "equipment_id": "PLC01",
  "material_code": "MAT001",
  "quantity": 10.5,
  "timestamp": "2025-02-06T10:30:00"
}

Response:
{
  "status": "success",
  "message": "Validation passed",
  "data": { ... }
}
```

## 6. Get MO List (Protected)
```
GET /api/scada/mo-list?equipment_id=PLC01&status=planned&limit=50&offset=0
Authorization: Bearer {token}

Response:
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

## 7. Acknowledge MO (Protected)
```
POST /api/scada/mo/123/acknowledge
Authorization: Bearer {token}
Content-Type: application/json

Body:
{
  "equipment_id": "PLC01",
  "status": "acknowledged",
  "timestamp": "2025-02-06T08:00:00"
}

Response:
{
  "status": "success",
  "message": "MO acknowledged successfully",
  "mo_id": 123
}
```

## 8. Update MO Status (Protected)
```
POST /api/scada/mo/123/update-status
Authorization: Bearer {token}
Content-Type: application/json

Body:
{
  "equipment_id": "PLC01",
  "status": "progress",
  "date_start_actual": "2025-02-06T08:00:00",
  "date_end_actual": "2025-02-06T16:00:00",
  "message": "Production started"
}

Response:
{
  "status": "success",
  "message": "MO status updated successfully",
  "mo_id": 123
}
```

## 9. Mark MO Done (Protected)
```
POST /api/scada/mo/123/mark-done
Authorization: Bearer {token}
Content-Type: application/json

Body:
{
  "equipment_id": "PLC01",
  "date_end_actual": "2025-02-06T16:00:00",
  "message": "Production completed"
}

Response:
{
  "status": "success",
  "message": "Manufacturing order marked as done",
  "mo_id": "MO/2025/001"
}
```

## 10. Get Equipment Status (Protected)
```
GET /api/scada/equipment/PLC01
Authorization: Bearer {token}

Response:
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

# ============================================================================
# ERROR HANDLING
# ============================================================================

```javascript
// Standard error format
{
  "status": "error",
  "message": "Deskripsi error yang jelas"
}

// Contoh handling di Vue
async function apiCall(endpoint, method = 'GET', body = null) {
  try {
    const response = await fetch(`${apiBaseUrl}${endpoint}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token.value}`,
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.message || `HTTP ${response.status}`);
    }
    
    if (data.status === 'error') {
      throw new Error(data.message);
    }
    
    return data;
  } catch (error) {
    // Show error to user
    showErrorNotification(error.message);
    throw error;
  }
}
```

# ============================================================================
# AXIOS ALTERNATIVE (More Modern)
# ============================================================================

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8069/api/scada',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('scada_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle errors globally
api.interceptors.response.use(
  (response) => {
    if (response.data.status === 'error') {
      throw new Error(response.data.message);
    }
    return response.data;
  },
  (error) => {
    console.error('API Error:', error);
    throw error;
  }
);

// Usage in Vue component
const { data } = await api.post('/material-consumption', {
  equipment_id: 'PLC01',
  material_code: 'MAT001',
  quantity: 10.5,
  timestamp: new Date().toISOString(),
});

console.log(data); // { status: 'success', message: '...', record_id: 123 }
```

# ============================================================================
# TESTING
# ============================================================================

```bash
# Test health endpoint (public, no auth needed)
curl -X GET http://localhost:8069/api/scada/health

# Test material consumption (needs token)
curl -X POST http://localhost:8069/api/scada/material-consumption \
  -H "Authorization: Bearer 2" \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_id": "PLC01",
    "material_code": "MAT001",
    "quantity": 10.5,
    "timestamp": "2025-02-06T10:30:00"
  }'

# Test MO list
curl -X GET "http://localhost:8069/api/scada/mo-list?equipment_id=PLC01" \
  -H "Authorization: Bearer 2"
```

"""
