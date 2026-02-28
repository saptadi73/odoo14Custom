# -*- coding: utf-8 -*-
# Migration: Add duration field to scada.equipment.failure model
# Version: 7.0.59

def migrate(cr, version):
    """
    Add duration field (Char) to scada.equipment.failure table
    This field stores failure duration in hh:mm format
    """
    cr.execute("""
        ALTER TABLE scada_equipment_failure 
        ADD COLUMN IF NOT EXISTS duration VARCHAR;
    """)
    
    # Optional: Add computed field duration_minutes for analysis
    # This will be computed automatically via ORM
