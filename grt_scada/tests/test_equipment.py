"""
Test SCADA Equipment model
"""

from odoo.tests import TransactionCase, tagged


@tagged('scada', 'equipment')
class TestScadaEquipment(TransactionCase):
    """Test cases untuk SCADA Equipment model"""

    def setUp(self):
        super().setUp()
        self.equipment_model = self.env['scada.equipment']

    def test_create_equipment(self):
        """Test creating a new equipment"""
        equipment = self.equipment_model.create({
            'name': 'Test Equipment',
            'equipment_code': 'TEST01',
            'equipment_type': 'plc',
            'manufacturer': 'OMRON',
            'protocol': 'modbus',
            'ip_address': '192.168.1.10',
            'port': 502,
        })
        self.assertEqual(equipment.name, 'Test Equipment')
        self.assertEqual(equipment.equipment_code, 'TEST01')
        self.assertEqual(equipment.connection_status, 'disconnected')

    def test_equipment_unique_code(self):
        """Test equipment code uniqueness"""
        self.equipment_model.create({
            'name': 'Equipment 1',
            'equipment_code': 'UNIQUE01',
            'equipment_type': 'plc',
        })

        with self.assertRaises(Exception):
            self.equipment_model.create({
                'name': 'Equipment 2',
                'equipment_code': 'UNIQUE01',
                'equipment_type': 'plc',
            })

    def test_test_connection(self):
        """Test connection test method"""
        equipment = self.equipment_model.create({
            'name': 'Test Equipment',
            'equipment_code': 'TEST02',
            'equipment_type': 'plc',
            'ip_address': '192.168.1.10',
            'port': 502,
        })

        result = equipment.test_connection()
        self.assertEqual(result['status'], 'success')
        self.assertEqual(equipment.connection_status, 'connected')

    def test_equipment_inactive(self):
        """Test inactive equipment"""
        equipment = self.equipment_model.create({
            'name': 'Inactive Equipment',
            'equipment_code': 'INACTIVE01',
            'equipment_type': 'plc',
            'is_active': False,
        })
        self.assertFalse(equipment.is_active)
