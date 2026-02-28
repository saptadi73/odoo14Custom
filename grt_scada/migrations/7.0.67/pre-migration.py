# -*- coding: utf-8 -*-
# Migration: ensure duration fields exist in scada.equipment.failure
# Version: 7.0.67


def migrate(cr, version):
    """Create missing columns required by stored duration fields."""
    cr.execute(
        """
        ALTER TABLE scada_equipment_failure
        ADD COLUMN IF NOT EXISTS duration VARCHAR;
        """
    )
    cr.execute(
        """
        ALTER TABLE scada_equipment_failure
        ADD COLUMN IF NOT EXISTS duration_minutes INTEGER;
        """
    )
