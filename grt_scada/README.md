# SCADA for Odoo Manufacturing Module

SCADA (Supervisory Control and Data Acquisition) module for Odoo 14 - Custom manufacturing integration with PLC/Equipment monitoring and Middleware API support.

## Overview

This module provides a comprehensive SCADA solution that integrates Odoo Manufacturing (MRP) with industrial equipment such as PLCs, sensors, and controllers. It enables real-time data acquisition, equipment monitoring, and bi-directional communication via REST API for middleware integration.

## Features

### Core Features
- **Equipment/PLC Management** - Configure and monitor PLCs and industrial equipment
- **Material Consumption via MO** - Middleware updates MO component consumption directly
- **Manufacturing Order Sync** - Synchronize manufacturing orders between Odoo and equipment/middleware
- **Sensor Data Collection** - Collect and monitor real-time sensor readings
- **Equipment Failure Report** - Pencatatan dan analisis failure per equipment (list, pivot, graph)
- **Middleware API** - REST API endpoints for middleware communication
- **API Logging** - Comprehensive logging of all API calls for audit trail

### Technical Features
- Role-based Access Control (Manager, Operator, Technician)
- Automated data sync and retry mechanism
- Equipment connection status monitoring
- Data validation and error handling
- Scheduled tasks (Cron) for background operations
- Demo data for testing

## Module Structure

```
grt_scada/
├── models/              # Data models
│   ├── scada_base.py               # Abstract base model
│   ├── scada_equipment.py          # Equipment/PLC configuration
│   ├── scada_material_consumption.py  # Legacy (no direct input)
│   ├── scada_mo_data.py            # Manufacturing order data
│   ├── scada_sensor_reading.py      # Sensor readings
│   └── scada_api_log.py            # API call logs
│
├── routes/              # API endpoints
│   └── mo_data_route.py              # GET: Manufacturing order endpoint
│
├── services/            # Business logic layer
│   ├── middleware_service.py    # Middleware communication
│   ├── data_converter.py        # Data format conversion
│   └── validation_service.py    # Input validation
│
├── views/               # UI Views
│   ├── menu.xml                 # Navigation menu
│   ├── scada_equipment_view.xml # Equipment UI
│   ├── scada_material_consumption_view.xml  # Legacy (not loaded)
│   ├── scada_mo_view.xml        # Manufacturing Order UI
│   ├── scada_sensor_reading_view.xml  # Sensor UI
│   └── scada_api_log_view.xml   # API Log UI
│
├── security/            # Access Control
│   ├── ir.model.access.csv  # Record access rules
│   └── ir.rule.xml          # Field-level rules
│
├── data/                # Demo and configuration data
│   ├── demo_data.xml    # Demo equipment
│   └── ir_cron.xml      # Scheduled tasks
│
├── tests/               # Unit tests
├── reports/             # Report definitions
└── static/              # Static assets (CSS, JS)
```

## API Endpoints

### Material Consumption API

**POST /api/scada/material-consumption**
- Apply material consumption directly to MO raw moves (no SCADA consumption record stored)
- Auth: Bearer token required
- Parameters:
  - `equipment_id`: Equipment code (required)
  - `product_id`: Product variant ID (required if `product_tmpl_id` not provided)
  - `product_tmpl_id`: Product template ID (optional)
  - `quantity`: Consumption quantity (required)
  - `timestamp`: ISO format timestamp (required)
  - `batch_number`: Optional batch identifier
  - `api_request_id`: Optional request ID

Example:
```json
{
    "equipment_id": "PLC01",
    "product_id": 123,
    "quantity": 10.5,
    "timestamp": "2025-02-06T10:30:00",
    "batch_number": "BATCH_001"
}
```

### Manufacturing Order Data API

**GET /api/scada/mo-list**
- Get manufacturing orders for equipment
- Auth: Bearer token required
- Query parameters:
  - `equipment_id`: Equipment code (required)
  - `status`: Optional status filter (planned, progress, done)
  - `limit`: Max records (default: 50)
  - `offset`: Pagination offset (default: 0)

Example:
```
GET /api/scada/mo-list?equipment_id=PLC01&status=planned&limit=10
```

### Failure Report API (Extension Module)

Jika module `grt_scada_failure_report` di-install, tersedia endpoint tambahan:

- `POST /api/scada/failure-report`
- `GET /scada/failure-report/input`
- `POST /scada/failure-report/submit`

Body minimal untuk endpoint API:

```json
{
  "equipment_code": "PLC01",
  "description": "Motor overload",
  "date": "2026-02-15 08:30:00"
}
```

## Installation

1. Place module in Odoo addons directory
2. Update module list in Odoo
3. Install `grt_scada` module
4. Configure equipment in SCADA > Equipment menu
5. Create API users with appropriate roles

## Configuration

### Equipment Setup
1. Go to SCADA > Equipment > Equipment List
2. Click Create
3. Fill in:
   - Equipment Name
   - Equipment Code (unique ID)
   - Equipment Type (PLC, Sensor, etc.)
   - Connection settings (IP, Port, Protocol)
  - Note: choose Protocol = Middleware if the device is handled by middleware; IP/Port are not required and status stays Disconnected
4. Test connection using "Test Connection" button

### User Roles
- **SCADA Manager**: Full access to all SCADA operations
- **SCADA Operator**: Read-only access + can acknowledge MO data
- **SCADA Technician**: Can record sensor readings and handle SCADA operations

## API Security

- All API endpoints require bearer token authentication
- Token should be passed in Authorization header: `Authorization: Bearer <token>`
- Each API call is logged in API Logs for audit trail

## Scheduled Tasks

The module includes automated background tasks:
- **Retry Failed Syncs**: Every 30 minutes
- **Sync Equipment Status**: Every hour
- **Cleanup Old Logs**: Daily (disabled by default, can be enabled)

## Models Overview

### SCADA Equipment
Manages physical equipment connected to system
- Connection status monitoring
- Protocol configuration (Modbus, MQTT, HTTP, TCP/IP, OPC-UA, Middleware)
- Production line association
- Last connection tracking

### SCADA Material Consumption (Deprecated)
Consumption is applied directly to MO raw moves; SCADA does not store consumption records.

### SCADA MO Data
Manages manufacturing order synchronization
- Bidirectional sync with equipment/middleware
- Equipment assignment and scheduling
- Actual vs. planned dates tracking
- Status codes for middleware (0-9 mapping)

### SCADA Sensor Reading
Collects real-time sensor data
- Multiple sensor types (Temperature, Pressure, Humidity, Flow, etc.)
- Threshold-based status alerts (Normal, Warning, Critical)
- Timestamp tracking for analysis

### SCADA API Log
Comprehensive API call logging
- Request/response data capture
- Performance metrics (response time)
- Error tracking and debugging
- Source IP and user agent logging

## Development

### Adding Custom Fields

Models inherit from `scada.base` which provides:
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `external_id`: Integration ID
- `source_system`: Data source tracking
- `sync_status`: Synchronization status
- `error_message`: Error tracking

### Adding New API Endpoints

Create new file in `routes/` directory:
```python
from odoo import http
from odoo.http import request

class MyCustomRoute(http.Controller):
    @http.route('/api/scada/my-endpoint', type='json', auth='bearer', methods=['POST'])
    def my_endpoint(self, **kwargs):
        # Implementation
        return {'status': 'success'}
```

Register in `routes/__init__.py`

## Testing

Run unit tests:
```bash
python -m pytest tests/
```

Test in Odoo:
1. Go to SCADA menu
2. Create demo equipment
3. Test API endpoints using curl or Postman
4. Check API Logs for verification

## Dependencies

### Python Packages
- `requests` - HTTP library for middleware communication
- `python-dateutil` - Date/time utilities

### Odoo Modules
- `manufacturing` - Manufacturing/MRP module
- `stock` - Inventory management
- `mrp` - Production planning
- `web` - Web interface
- `base` - Base Odoo module

## Support

For issues or feature requests, contact:
**PT. Gagak Rimang Teknologi**
Website: https://rimang.id

## License

LGPL-3 (GNU Lesser General Public License v3)

## Version History

### 1.0.0 (2025-02-06)
- Initial release
- Core SCADA functionality
- MO sync with consumption applied directly to MO moves
- Middleware API integration
- Role-based access control
