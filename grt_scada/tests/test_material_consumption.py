"""
Test SCADA Material Consumption model
"""

from odoo.tests import TransactionCase, tagged
from datetime import datetime


@tagged('scada', 'material_consumption')
class TestScadaMaterialConsumption(TransactionCase):
    """Test cases untuk SCADA Material Consumption model"""

    def setUp(self):
        super().setUp()
        self.consumption_model = self.env['scada.material.consumption']
        self.equipment_model = self.env['scada.equipment']
        self.product_model = self.env['product.product']

        # Create test equipment
        self.equipment = self.equipment_model.create({
            'name': 'Test Equipment',
            'equipment_code': 'TEST01',
            'equipment_type': 'plc',
        })

        # Create test material
        self.material = self.product_model.create({
            'name': 'Test Material',
            'default_code': 'MAT001',
            'type': 'product',
        })

    def test_create_consumption(self):
        """Test creating material consumption record"""
        consumption = self.consumption_model.create({
            'equipment_id': self.equipment.id,
            'material_id': self.material.id,
            'quantity': 10.5,
            'timestamp': datetime.now(),
            'status': 'draft',
        })
        self.assertEqual(consumption.quantity, 10.5)
        self.assertEqual(consumption.status, 'draft')

    def test_consumption_validation(self):
        """Test material consumption validation"""
        with self.assertRaises(Exception):
            self.consumption_model.create({
                'equipment_id': self.equipment.id,
                'material_id': self.material.id,
                'quantity': -5,  # Negative quantity
                'timestamp': datetime.now(),
            })

    def test_action_validate(self):
        """Test validating consumption"""
        consumption = self.consumption_model.create({
            'equipment_id': self.equipment.id,
            'material_id': self.material.id,
            'quantity': 10.5,
            'timestamp': datetime.now(),
            'status': 'recorded',
        })

        consumption.action_validate()
        self.assertEqual(consumption.status, 'validated')

    def test_retry_sync(self):
        """Test retry sync"""
        consumption = self.consumption_model.create({
            'equipment_id': self.equipment.id,
            'material_id': self.material.id,
            'quantity': 10.5,
            'timestamp': datetime.now(),
            'sync_status': 'error',
            'error_message': 'Test error',
        })

        consumption.retry_sync()
        self.assertEqual(consumption.sync_status, 'pending')
        self.assertFalse(consumption.error_message)
