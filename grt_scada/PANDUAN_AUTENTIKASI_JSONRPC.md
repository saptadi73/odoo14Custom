# Panduan Autentikasi JSON-RPC untuk Vue.js

**Bahasa**: Bahasa Indonesia
**Platform**: Odoo 14 + Vue.js 3
**Protokol**: Bearer Token (Session-based)

---

## 📋 Daftar Isi

1. [Konsep Autentikasi](#konsep-autentikasi)
2. [Setup Awal](#setup-awal)
3. [Implementasi Vue.js](#implementasi-vuejs)
4. [Troubleshooting](#troubleshooting)

---

## Konsep Autentikasi

### Mengapa Tidak Ada "Generate API Key"?

Odoo 14 **tidak memiliki** fitur "Generate API Key" seperti di Odoo 16+. 
Solusinya: gunakan **Session ID** sebagai token autentikasi.

### Cara Kerjanya

```
1. User Login → Odoo buat session
2. Session ID disimpan di cookies browser
3. Gunakan Session ID sebagai Bearer token
4. API memvalidasi token
5. Akses granted!
```

### Alur Autentikasi

```
┌─────────────────────────────────────────────┐
│ User Login ke Odoo                          │
│ (Melalui form standard /web/login)         │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│ Odoo membuat Session (ID = 2)               │
│ Session disimpan di:                         │
│ - Browser cookies                            │
│ - Backend session storage                   │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│ Gunakan Token di API Call:                   │
│ Authorization: Bearer 2                      │
│ (Session ID menjadi token)                  │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│ API Validasi Token                          │
│ ✓ Token valid → proceed                     │
│ ✗ Token invalid → 401 Unauthorized          │
└──────────────────────────────────────────────┘
```

---

## Setup Awal

### Step 1: Login Odoo via Browser

```html
<!-- Di halaman login Odoo -->
http://localhost:8069/web/login
```

1. Masukkan username (email): `admin@example.com`
2. Masukkan password
3. Pilih database
4. Klik "Log in"

Setelah login berhasil, session ID disimpan otomatis di cookies.

### Step 2: Dapatkan Session ID (untuk API client non-browser)

Jika menggunakan middleware/API client (bukan browser), dapatkan session ID:

```python
import requests
import json

def get_session_id(host, db, username, password):
    """Dapatkan session ID dari Odoo"""
    url = f'{host}/web/session/authenticate'
    
    payload = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
            'db': db,
            'login': username,
            'password': password
        }
    }
    
    response = requests.post(
        url,
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    result = response.json()
    
    if 'error' in result:
        raise Exception(f"Login error: {result['error']}")
    
    # Session ID ada di cookies
    session_id = response.cookies.get('session_id')
    return session_id

# Gunakan
try:
    token = get_session_id(
        'http://localhost:8069',
        'your_database',
        'admin@example.com',
        'password'
    )
    print(f'Token: {token}')
except Exception as e:
    print(f'Error: {e}')
```

### Step 3: Gunakan Token di API Calls

Simpan token di localStorage (untuk browser):

```javascript
// Setelah login successful
localStorage.setItem('scada_token', '2');  // Session ID

// Gunakan di API calls
const token = localStorage.getItem('scada_token');
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};
```

---

## Implementasi Vue.js

### Solusi 1: Composable Function (Recommended)

**File**: `src/composables/useScadaApi.js`

```javascript
import { ref, computed } from 'vue';

export function useScadaApi(baseUrl = 'http://localhost:8069') {
  const token = ref(localStorage.getItem('scada_token') || null);
  const loading = ref(false);
  const error = ref(null);
  
  const isAuthenticated = computed(() => token.value !== null);
  
  /**
   * Perform API call dengan auto error handling
   */
  const apiCall = async (endpoint, method = 'GET', body = null) => {
    if (!token.value) {
      throw new Error('Not authenticated. Please login first.');
    }
    
    loading.value = true;
    error.value = null;
    
    try {
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
      
      const response = await fetch(
        `${baseUrl}/api/scada${endpoint}`,
        options
      );
      
      // Check if response is valid JSON
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        throw new Error(`Invalid response type: ${contentType}`);
      }
      
      const data = await response.json();
      
      // Handle API error response
      if (data.status === 'error') {
        error.value = data.message;
        throw new Error(data.message);
      }
      
      return data;
      
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  /**
   * Set token (biasanya setelah login)
   */
  const setToken = (newToken) => {
    token.value = newToken;
    localStorage.setItem('scada_token', newToken);
  };
  
  /**
   * Clear token (logout)
   */
  const clearToken = () => {
    token.value = null;
    localStorage.removeItem('scada_token');
  };
  
  return {
    token,
    isAuthenticated,
    loading,
    error,
    apiCall,
    setToken,
    clearToken,
  };
}
```

### Solusi 2: Menggunakan di Vue Component

```vue
<template>
  <div class="scada-dashboard">
    <!-- Login Form -->
    <div v-if="!isAuthenticated" class="login-card">
      <h2>Login SCADA</h2>
      <form @submit.prevent="handleLogin">
        <input 
          v-model="loginForm.username" 
          type="email" 
          placeholder="Email"
          required
        />
        <input 
          v-model="loginForm.password" 
          type="password" 
          placeholder="Password"
          required
        />
        <button type="submit" :disabled="logging-in">
          {{ loginInProgress ? 'Logging in...' : 'Login' }}
        </button>
        <p v-if="loginError" class="error">{{ loginError }}</p>
      </form>
    </div>
    
    <!-- Dashboard (after login) -->
    <div v-else class="dashboard">
      <div class="welcome">
        <p>✓ Authenticated</p>
        <button @click="handleLogout">Logout</button>
      </div>
      
      <!-- Health Check -->
      <div class="card">
        <h3>System Status</h3>
        <button @click="checkHealth">Check Health</button>
        <p v-if="healthStatus">{{ healthStatus.message }}</p>
      </div>
      
      <!-- Material Consumption Form -->
      <div class="card">
        <h3>Catat Konsumsi Material</h3>
        <form @submit.prevent="saveMaterialConsumption">
          <input 
            v-model="consumption.equipment_id" 
            placeholder="Kode Equipment (contoh: PLC01)"
            required 
          />
          <input 
            v-model="consumption.material_code" 
            placeholder="Kode Material (contoh: MAT001)"
            required 
          />
          <input 
            v-model.number="consumption.quantity" 
            type="number" 
            placeholder="Jumlah"
            required 
          />
          <input 
            v-model="consumption.timestamp" 
            type="datetime-local"
            :value="defaultTimestamp"
            required 
          />
          <button type="submit" :disabled="submitting">
            {{ submitting ? 'Saving...' : 'Simpan' }}
          </button>
        </form>
        <p v-if="consumptionResult" :class="consumptionResult.status">
          {{ consumptionResult.message }}
        </p>
      </div>
      
      <!-- Error Display -->
      <div v-if="error" class="error-alert">
        <strong>Error:</strong> {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useScadaApi } from '@/composables/useScadaApi';

// API Composable
const { 
  token, 
  isAuthenticated, 
  loading, 
  error, 
  apiCall,
  setToken,
  clearToken 
} = useScadaApi();

// Login State
const loginForm = ref({
  username: '',
  password: '',
});
const loginError = ref(null);
const loginInProgress = ref(false);

// Dashboard State
const healthStatus = ref(null);
const consumption = ref({
  equipment_id: '',
  material_code: '',
  quantity: 0,
  timestamp: new Date().toISOString().slice(0, 16),
});
const consumptionResult = ref(null);
const submitting = ref(false);

// Computed
const defaultTimestamp = computed(() => {
  return new Date().toISOString().slice(0, 16);
});

// Methods
const handleLogin = async () => {
  loginInProgress.value = true;
  loginError.value = null;
  
  try {
    // Authenticate dengan Odoo
    const response = await fetch('http://localhost:8069/web/session/authenticate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'call',
        params: {
          db: 'your_database', // Set database name
          login: loginForm.value.username,
          password: loginForm.value.password
        }
      })
    });
    
    const result = await response.json();
    
    if (result.error) {
      loginError.value = result.error.data?.message || 'Login failed';
      return;
    }
    
    // Dapatkan session ID dari response
    const sessionId = result.result?.uid || '2'; // Default fallback
    setToken(sessionId);
    
    // Clear form
    loginForm.value = { username: '', password: '' };
    
  } catch (err) {
    loginError.value = err.message;
  } finally {
    loginInProgress.value = false;
  }
};

const handleLogout = () => {
  clearToken();
  healthStatus.value = null;
  consumptionResult.value = null;
  consumption.value = {
    equipment_id: '',
    material_code: '',
    quantity: 0,
    timestamp: new Date().toISOString().slice(0, 16),
  };
};

const checkHealth = async () => {
  try {
    healthStatus.value = await apiCall('/health');
  } catch (err) {
    console.error('Health check failed:', err);
  }
};

const saveMaterialConsumption = async () => {
  submitting.value = true;
  consumptionResult.value = null;
  
  try {
    const result = await apiCall('/material-consumption', 'POST', {
      equipment_id: consumption.value.equipment_id,
      material_code: consumption.value.material_code,
      quantity: consumption.value.quantity,
      timestamp: consumption.value.timestamp,
    });
    
    consumptionResult.value = {
      status: result.status,
      message: result.message,
    };
    
    if (result.status === 'success') {
      // Reset form
      consumption.value = {
        equipment_id: '',
        material_code: '',
        quantity: 0,
        timestamp: new Date().toISOString().slice(0, 16),
      };
    }
  } catch (err) {
    consumptionResult.value = {
      status: 'error',
      message: err.message,
    };
  } finally {
    submitting.value = false;
  }
};

// Initialize
onMounted(() => {
  // Check if already have token
  if (!token.value) {
    loginError.value = 'Please login first';
  }
});
</script>

<style scoped>
.scada-dashboard {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.login-card, .card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  background: #f9f9f9;
}

h2, h3 {
  margin-top: 0;
  color: #333;
}

form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

input, button {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font: inherit;
}

button {
  background: #007bff;
  color: white;
  cursor: pointer;
  font-weight: bold;
}

button:hover {
  background: #0056b3;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.error {
  color: #d32f2f;
  margin: 10px 0 0 0;
}

.error-alert {
  background: #ffebee;
  border: 1px solid #d32f2f;
  color: #d32f2f;
  padding: 12px;
  border-radius: 4px;
  margin-top: 20px;
}

.success {
  color: #388e3c;
}

.welcome {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #e8f5e9;
  border: 1px solid #388e3c;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}
</style>
```

---

## Solusi 3: Axios Interceptor

Alternatif menggunakan Axios untuk request management yang lebih advanced:

```javascript
// src/http-client.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8069/api/scada',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - tambah token otomatis
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('scada_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle error globally
apiClient.interceptors.response.use(
  (response) => {
    // Check API status
    if (response.data?.status === 'error') {
      return Promise.reject(new Error(response.data.message));
    }
    return response.data; // Return data directly (tidak response object)
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token invalid/expired
      localStorage.removeItem('scada_token');
      window.location.href = '/login'; // Redirect ke login
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

Penggunaan:

```javascript
import apiClient from '@/http-client';

// Dalam Vue component
async function loadMOList() {
  try {
    const data = await apiClient.get('/mo-list?equipment_id=PLC01');
    console.log('MO List:', data.data); // data.data karena response sudah di-extract
  } catch (error) {
    console.error('Error:', error.message);
  }
}
```

---

## Troubleshooting

### Problem 1: 401 Unauthorized

```
Error: { status: 'error', message: 'Unauthorized' }
```

**Solusi**:
```javascript
// Check token
const token = localStorage.getItem('scada_token');
console.log('Current token:', token);

// Jika kosong, login lagi
if (!token) {
  window.location.href = '/web/login';
}

// Jika ada token tapi masih 401, session expired
// -> Clear token dan login ulang
localStorage.removeItem('scada_token');
```

### Problem 2: CORS Error

```
Error: Access to XMLHttpRequest blocked by CORS policy
```

**Solusi** (di Odoo):

Tambah ke `odoo.conf`:
```ini
cors_enabled = true
cors_allowed_origins = http://localhost:3000,http://localhost:5173
```

Atau di code:
```python
# controllers/__init__.py
import werkzeug.http
from odoo import http

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
}

@http.route('/api/scada/<path:path>', methods=['OPTIONS'])
def cors_preflight(path):
    return '', 200, CORS_HEADERS
```

### Problem 3: Token Expired

```
Error: Session invalid
```

**Solusi**:
```javascript
// Implement token refresh
const MAX_TOKEN_AGE = 24 * 60 * 60 * 1000; // 24 hours

function checkTokenExpiry() {
  const lastLogin = localStorage.getItem('last_login_time');
  const now = Date.now();
  
  if (lastLogin && (now - parseInt(lastLogin)) > MAX_TOKEN_AGE) {
    // Token expired
    localStorage.removeItem('scada_token');
    // Redirect to login
  }
}

// Simpan waktu login
localStorage.setItem('last_login_time', Date.now());
```

### Problem 4: Network Error

```
Error: fetch failed / Network error
```

**Solusi**:
```javascript
async function apiCallWithRetry(endpoint, method = 'GET', body = null, maxRetry = 3) {
  for (let attempt = 1; attempt <= maxRetry; attempt++) {
    try {
      console.log(`Attempt ${attempt}/${maxRetry}...`);
      
      const response = await fetch(
        `http://localhost:8069/api/scada${endpoint}`,
        {
          method,
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: body ? JSON.stringify(body) : undefined,
          timeout: 5000, // 5 second timeout
        }
      );
      
      return await response.json();
      
    } catch (error) {
      if (attempt === maxRetry) throw error;
      
      // Wait sebelum retry (exponential backoff)
      const delay = 1000 * Math.pow(2, attempt - 1);
      console.log(`Retrying after ${delay}ms...`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
}
```

---

## Testing Autentikasi

### Test 1: Browser Console

```javascript
// Di browser console setelah login
const token = localStorage.getItem('scada_token');
console.log('Token:', token);

// Test API call
fetch('http://localhost:8069/api/scada/health', {
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(r => r.json())
.then(d => console.log(d));
```

### Test 2: cURL

```bash
# Set token
TOKEN=2

# Health check (public - tidak perlu token)
curl http://localhost:8069/api/scada/health

# Material consumption (perlu token)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8069/api/scada/material-consumption/{id}
```

### Test 3: Python

```python
import requests

TOKEN = '2'
BASE_URL = 'http://localhost:8069'

# API call dengan token
headers = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}

response = requests.get(
    f'{BASE_URL}/api/scada/health',
    headers=headers
)

print('Status:', response.status_code)
print('Response:', response.json())
```

---

## Checklist Implementasi

- [ ] Login page terhubung ke Odoo
- [ ] Token disimpan di localStorage
- [ ] Token dikirim di header Authorization
- [ ] Health endpoint responsive
- [ ] Material consumption endpoint berfungsi
- [ ] Error handling diterapkan
- [ ] Loading state ditampilkan
- [ ] Token refresh/logout implemented
- [ ] CORS configured (jika frontend berbeda domain)
- [ ] Production HTTPS ready

---

## Ringkasan

| Bagian | Detail |
|--------|--------|
| **Auth Type** | Session-based Bearer Token |
| **Token Source** | Odoo Session ID |
| **Storage** | localStorage (browser) |
| **Renewal** | Auto via session (jika masih login) |
| **Expiry** | Same as Odoo session timeout |
| **Format** | `Authorization: Bearer {sessionID}` |
| **Implementation** | Composable + Axios/Fetch |

---

**Selesai!** Anda siap mengimplementasikan JSON-RPC autentikasi di Vue.js.

Untuk pertanyaan lebih lanjut, lihat [API_SPEC.md](API_SPEC.md) atau [JSONRPC_VUEJS_GUIDE.md](JSONRPC_VUEJS_GUIDE.md).
