"""
SCADA Equipment Model
Model untuk konfigurasi equipment/PLC yang terhubung dengan sistem
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ScadaEquipment(models.Model):
    """Model untuk SCADA Equipment/PLC Configuration"""
    _name = 'scada.equipment'
    _description = 'SCADA Equipment/PLC Configuration'
    _order = 'name asc'

    name = fields.Char(
        string='Equipment Name',
        required=True,
        help='Nama equipment/PLC (contoh: PLC01, INJECTOR_01)'
    )
    equipment_code = fields.Char(
        string='Equipment Code',
        required=True,
        unique=True,
        help='Kode unik equipment untuk identifikasi'
    )
    equipment_type = fields.Selection(
        [
            ('plc', 'PLC'),
            ('sensor', 'Sensor'),
            ('controller', 'Controller'),
            ('injector', 'Injection Machine'),
            ('press', 'Press Machine'),
            ('other', 'Other'),
        ],
        string='Equipment Type',
        required=True,
        help='Tipe equipment'
    )
    manufacturer = fields.Char(
        string='Manufacturer',
        help='Produsen equipment (contoh: OMRON, Siemens)'
    )
    model_number = fields.Char(
        string='Model Number',
        help='Nomor model equipment'
    )
    serial_number = fields.Char(
        string='Serial Number',
        help='Nomor seri equipment'
    )

    # Connection settings
    ip_address = fields.Char(
        string='IP Address',
        help='IP address equipment di jaringan'
    )
    port = fields.Integer(
        string='Port',
        help='Port untuk komunikasi'
    )
    protocol = fields.Selection(
        [
            ('modbus', 'Modbus'),
            ('opcua', 'OPC-UA'),
            ('mqtt', 'MQTT'),
            ('http', 'HTTP/REST'),
            ('tcp', 'TCP/IP'),
            ('other', 'Other'),
        ],
        string='Protocol',
        help='Protokol komunikasi dengan equipment'
    )

    # Odoo Integration
    production_line_id = fields.Many2one(
        'mrp.workcenter',
        string='Work Center',
        help='Work center yang terkait dengan equipment ini'
    )
    is_active = fields.Boolean(
        string='Is Active',
        default=True,
        help='Tandakan jika equipment aktif'
    )

    # Status monitoring
    last_connected = fields.Datetime(
        string='Last Connected',
        readonly=True,
        help='Waktu last connection dengan device'
    )
    connection_status = fields.Selection(
        [
            ('connected', 'Connected'),
            ('disconnected', 'Disconnected'),
            ('error', 'Error'),
        ],
        string='Connection Status',
        default='disconnected',
        readonly=True,
        help='Status koneksi current'
    )

    # Sync status with middleware
    sync_status = fields.Selection(
        [
            ('pending', 'Pending'),
            ('synced', 'Synced'),
            ('error', 'Error'),
            ('failed', 'Failed'),
        ],
        string='Sync Status',
        default='pending',
        help='Status sinkronisasi dengan sistem eksternal'
    )
    error_message = fields.Text(
        string='Error Message',
        help='Pesan error jika terjadi kesalahan'
    )

    notes = fields.Text(
        string='Notes',
        help='Catatan tambahan tentang equipment'
    )

    # Relations
    material_consumption_ids = fields.One2many(
        'scada.material.consumption',
        'equipment_id',
        string='Material Consumptions',
        help='Material consumption records dari equipment ini'
    )
    equipment_material_ids = fields.One2many(
        'scada.equipment.material',
        'equipment_id',
        string='Equipment Material Consumption',
        help='Mapping/consumption untuk OEE dan analitik'
    )
    mo_data_ids = fields.One2many(
        'scada.mo.data',
        'equipment_id',
        string='MO Data',
        help='Manufacturing order data dari equipment ini'
    )
    sensor_reading_ids = fields.One2many(
        'scada.sensor.reading',
        'equipment_id',
        string='Sensor Readings',
        help='Sensor reading dari equipment ini'
    )
    api_log_ids = fields.One2many(
        'scada.api.log',
        'equipment_id',
        string='API Logs',
        help='API call logs untuk equipment ini'
    )

    @api.constrains('ip_address', 'port', 'protocol')
    def _check_connection_settings(self):
        """Validate connection settings"""
        for record in self:
            if record.protocol in ['http', 'tcp', 'modbus']:
                if not record.ip_address:
                    raise ValidationError(
                        f"IP Address harus diisi untuk protocol {record.protocol}"
                    )
                if not record.port:
                    raise ValidationError(
                        f"Port harus diisi untuk protocol {record.protocol}"
                    )

    def update_connection_status(self, new_status, last_connected=None):
        """Update connection status"""
        from datetime import datetime
        self.write({
            'connection_status': new_status,
            'last_connected': last_connected or datetime.now(),
        })

    def test_connection(self):
        """Test connection ke equipment"""
        # TODO: Implement actual connection test logic
        self.update_connection_status('connected')
        return {
            'status': 'success',
            'message': f'Connection test successful for {self.name}'
        }

    # ===== XML-RPC Compatible Methods =====
    
    @api.model
    def get_equipment_status(self, equipment_code):
        """
        Get status equipment via XML-RPC
        
        XML-RPC Usage:
            models.execute_kw(db, uid, pwd, 'scada.equipment', 
                             'get_equipment_status', ['PLC01'])
        """
        equipment = self.search([
            ('equipment_code', '=', equipment_code)
        ], limit=1)
        
        if not equipment:
            return {
                'status': 'error',
                'message': f'Equipment "{equipment_code}" not found',
            }
        
        return {
            'status': 'success',
            'data': {
                'id': equipment.id,
                'equipment_code': equipment.equipment_code,
                'name': equipment.name,
                'connection_status': equipment.connection_status,
                'is_active': equipment.is_active,
                'last_connected': equipment.last_connected.isoformat() if equipment.last_connected else None,
            }
        }

    @api.model
    def sync_equipment_status(self):
        """
        Sync status semua active equipment
        
        XML-RPC Usage:
            models.execute_kw(db, uid, pwd, 'scada.equipment', 
                             'sync_equipment_status', [])
        """
        try:
            equipment_list = self.search([
                ('is_active', '=', True)
            ])
            
            count = 0
            for equipment in equipment_list:
                equipment.test_connection()
                count += 1
            
            return {
                'status': 'success',
                'message': f'Synced {count} equipment records',
                'count': count,
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error: {str(e)}',
                'count': 0,
            }
