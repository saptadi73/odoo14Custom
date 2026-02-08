"""
SCADA XML-RPC Integration Guide
Complete implementation guide untuk mengintegrasikan Odoo 14 SCADA Module via XML-RPC
"""

# ============================================================================
# 1. AUTHENTICATION SETUP (Run once at the beginning)
# ============================================================================

import xmlrpc.client

# Configuration
ODOO_URL = 'http://localhost:8069'  # Ganti dengan URL Odoo Anda
DB_NAME = 'your_database_name'
USERNAME = 'admin@example.com'
PASSWORD = 'your_password'

# Authenticate and get session ID
try:
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(DB_NAME, USERNAME, PASSWORD, {})
    print(f"✓ Authentication successful. UID: {uid}")
except Exception as e:
    print(f"✗ Authentication failed: {e}")
    exit(1)

# Create models RPC endpoint
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')


# ============================================================================
# 2. HEALTH CHECK
# ============================================================================

def health_check():
    """Check apakah SCADA module running"""
    try:
        result = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'scada.health', 'check', []
        )
        print("✓ Health Check:", result)
        return result
    except Exception as e:
        print(f"✗ Health Check Error: {e}")
        return None


# ============================================================================
# 3. GET MODULE VERSION
# ============================================================================

def get_module_version():
    """Get SCADA module version"""
    try:
        result = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'scada.module', 'get_version', []
        )
        print("✓ Module Version:", result)
        return result
    except Exception as e:
        print(f"✗ Module Version Error: {e}")
        return None


# ============================================================================
# 4. CREATE MATERIAL CONSUMPTION
# ============================================================================

def create_material_consumption(payload):
    """
    Create material consumption record
    
    Args:
        payload: Dict with required fields
    """
    try:
        result = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'scada.material.consumption', 'create_from_api',
            [payload]
        )
        print("✓ Material Consumption Created:", result)
        return result
    except Exception as e:
        print(f"✗ Create Material Consumption Error: {e}")
        return None


# Example usage:
payload = {
    'equipment_id': 'PLC01',
    'material_code': 'MAT001',
    'quantity': 10.5,
    'timestamp': '2025-02-06T10:30:00',
    'batch_number': 'BATCH_001',
    'api_request_id': 'REQ_001',
    'notes': 'Material consumption from middleware'
}
# result = create_material_consumption(payload)


# ============================================================================
# 5. VALIDATE MATERIAL CONSUMPTION PAYLOAD
# ============================================================================

def validate_material_consumption(payload):
    """Validate payload sebelum create"""
    try:
        result = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'scada.material.consumption', 'validate_payload',
            [payload]
        )
        print("✓ Validation Result:", result)
        return result
    except Exception as e:
        print(f"✗ Validation Error: {e}")
        return None


# ============================================================================
# 6. GET MATERIAL CONSUMPTION BY ID
# ============================================================================

def get_material_consumption(record_id):
    """Get material consumption record"""
    try:
        result = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'scada.material.consumption', 'get_by_id',
            [record_id],
            {'fields': ['id', 'equipment_id', 'material_code', 'quantity', 
                       'timestamp', 'status', 'sync_status']}
        )
        print("✓ Material Consumption Data:", result)
        return result
    except Exception as e:
        print(f"✗ Get Material Consumption Error: {e}")
        return None


# ============================================================================
# 7. GET MO LIST FOR EQUIPMENT
# ============================================================================

def get_mo_list(equipment_code, status=None, limit=50, offset=0):
    """
    Get Manufacturing Order list untuk equipment
    
    Args:
        equipment_code: Equipment code (e.g., 'PLC01')
        status: Optional - 'planned', 'progress', 'done'
        limit: Max records to return
        offset: Pagination offset
    """
    try:
        kwargs = {'limit': limit, 'offset': offset}
        if status:
            kwargs['status'] = status
        
        result = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'scada.mo.data', 'get_mo_list_for_equipment',
            [equipment_code],
            kwargs
        )
        print(f"✓ MO List for {equipment_code}:", result)
        return result
    except Exception as e:
        print(f"✗ Get MO List Error: {e}")
        return None


# Example usage:
# result = get_mo_list('PLC01', status='planned', limit=50)


# ============================================================================
# 8. ACKNOWLEDGE MANUFACTURING ORDER
# ============================================================================

def acknowledge_mo(mo_record_id, equipment_code):
    """
    Acknowledge MO dari middleware
    
    Args:
        mo_record_id: MO Data record ID dari Odoo
        equipment_code: Equipment code
    """
    try:
        payload = {
            'equipment_id': equipment_code,
            'status': 'acknowledged',
            'timestamp': '2025-02-06T08:00:00'
        }
        
        result = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'scada.mo.data', 'acknowledge_mo',
            [mo_record_id, payload]
        )
        print("✓ MO Acknowledged:", result)
        return result
    except Exception as e:
        print(f"✗ Acknowledge MO Error: {e}")
        return None


# ============================================================================
# 9. UPDATE MO STATUS
# ============================================================================

def update_mo_status(mo_record_id, equipment_code, start_time=None, end_time=None):
    """
    Update MO status ke 'progress'
    
    Args:
        mo_record_id: MO Data record ID
        equipment_code: Equipment code
        start_time: Actual start time (ISO format)
        end_time: Actual end time (ISO format)
    """
    try:
        payload = {
            'equipment_id': equipment_code,
            'status': 'progress',
        }
        if start_time:
            payload['date_start_actual'] = start_time
        if end_time:
            payload['date_end_actual'] = end_time
        
        result = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'scada.mo.data', 'update_mo_status',
            [mo_record_id, payload]
        )
        print("✓ MO Status Updated:", result)
        return result
    except Exception as e:
        print(f"✗ Update MO Status Error: {e}")
        return None


# ============================================================================
# 10. MARK MO AS DONE
# ============================================================================

def mark_mo_done(mo_record_id, equipment_code, end_time=None):
    """
    Mark Manufacturing Order sebagai selesai
    
    Args:
        mo_record_id: MO Data record ID
        equipment_code: Equipment code
        end_time: Actual end time (ISO format)
    """
    try:
        payload = {
            'equipment_id': equipment_code,
        }
        if end_time:
            payload['date_end_actual'] = end_time
        
        result = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'scada.mo.data', 'mark_mo_done',
            [mo_record_id, payload]
        )
        print("✓ MO Marked as Done:", result)
        return result
    except Exception as e:
        print(f"✗ Mark MO Done Error: {e}")
        return None


# ============================================================================
# 11. GET EQUIPMENT STATUS
# ============================================================================

def get_equipment_status(equipment_code):
    """Get status dari specific equipment"""
    try:
        result = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'scada.equipment', 'get_equipment_status',
            [equipment_code]
        )
        print("✓ Equipment Status:", result)
        return result
    except Exception as e:
        print(f"✗ Get Equipment Status Error: {e}")
        return None


# ============================================================================
# 12. SYNC EQUIPMENT STATUS
# ============================================================================

def sync_equipment_status():
    """Sync status dari semua active equipment"""
    try:
        result = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'scada.equipment', 'sync_equipment_status',
            []
        )
        print("✓ Equipment Sync Result:", result)
        return result
    except Exception as e:
        print(f"✗ Sync Equipment Status Error: {e}")
        return None


# ============================================================================
# EXAMPLE: Complete Workflow
# ============================================================================

def example_complete_workflow():
    """
    Example workflow dari awal sampai akhir
    """
    print("\n" + "="*70)
    print("SCADA XML-RPC COMPLETE WORKFLOW EXAMPLE")
    print("="*70 + "\n")
    
    # 1. Health check
    print("1. Health Check:")
    health_check()
    
    # 2. Get module version
    print("\n2. Get Module Version:")
    get_module_version()
    
    # 3. Get equipment status
    print("\n3. Get Equipment Status:")
    get_equipment_status('PLC01')
    
    # 4. Get MO list
    print("\n4. Get MO List for Equipment:")
    mo_list_result = get_mo_list('PLC01', status='planned', limit=10)
    
    if mo_list_result and mo_list_result['status'] == 'success' and mo_list_result['data']:
        mo_record = mo_list_result['data'][0]
        mo_id = mo_record['id']
        
        # 5. Acknowledge MO
        print(f"\n5. Acknowledge MO (ID: {mo_id}):")
        acknowledge_mo(mo_id, 'PLC01')
        
        # 6. Update MO Status to progress
        print(f"\n6. Update MO Status to Progress (ID: {mo_id}):")
        update_mo_status(
            mo_id, 'PLC01',
            start_time='2025-02-06T08:00:00',
            end_time='2025-02-06T16:00:00'
        )
        
        # 7. Mark MO done
        print(f"\n7. Mark MO Done (ID: {mo_id}):")
        mark_mo_done(mo_id, 'PLC01', end_time='2025-02-06T16:00:00')
    
    # 8. Create material consumption
    print("\n8. Create Material Consumption:")
    material_payload = {
        'equipment_id': 'PLC01',
        'material_code': 'MAT001',
        'quantity': 10.5,
        'timestamp': '2025-02-06T14:30:00',
        'batch_number': 'BATCH_001',
    }
    mat_result = create_material_consumption(material_payload)
    
    if mat_result and mat_result['status'] == 'success':
        print(f"\n9. Get Material Consumption (ID: {mat_result['record_id']}):")
        get_material_consumption(mat_result['record_id'])


# ============================================================================
# Run Examples
# ============================================================================

if __name__ == '__main__':
    print("SCADA XML-RPC Integration Examples\n")
    
    # Uncomment untuk run example workflow
    # example_complete_workflow()
    
    # Atau run fungsi individual:
    health_check()
    get_module_version()
    get_equipment_status('PLC01')
