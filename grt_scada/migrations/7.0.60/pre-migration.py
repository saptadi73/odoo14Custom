# -*- coding: utf-8 -*-
# Migration: Add duration field to scada.equipment.failure
# Version: 7.0.60

def migrate(cr, version):
    """
    Add duration Char field to scada.equipment.failure table
    This allows manual input of failure duration in hh:mm format
    """
    # Add duration column if not exists
    cr.execute("""
        ALTER TABLE scada_equipment_failure 
        ADD COLUMN duration VARCHAR;
    """)
    
    # Add duration_minutes computed column (will be auto-managed by ORM)
    # Note: duration_minutes is a computed field, ORM handles it
