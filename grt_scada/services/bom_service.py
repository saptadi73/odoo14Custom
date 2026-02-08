"""
BoM Service
Business logic untuk mengambil data BoM beserta komponen
"""

import logging
from typing import Optional

_logger = logging.getLogger(__name__)


class BomService:
    """Service untuk data BoM"""

    def __init__(self, env):
        self.env = env

    def get_bom_list(
        self,
        bom_id: Optional[int] = None,
        product_id: Optional[int] = None,
        product_tmpl_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
        active: Optional[bool] = True,
    ):
        """
        Get list BoM dengan komponen.

        Args:
            bom_id: ID BoM (optional)
            product_id: ID product variant (optional)
            product_tmpl_id: ID product template (optional)
            limit: Batas record
            offset: Offset record
            active: True/False untuk filter aktif, None untuk semua
        """
        try:
            domain = []

            if active is True:
                domain.append(('active', '=', True))
            elif active is False:
                domain.append(('active', '=', False))

            if bom_id:
                domain.append(('id', '=', bom_id))

            if product_id:
                product = self.env['product.product'].browse(product_id)
                template_id = product.product_tmpl_id.id if product and product.exists() else None
                if template_id:
                    domain.extend(['|', ('product_id', '=', product_id), ('product_tmpl_id', '=', template_id)])
                else:
                    domain.append(('product_id', '=', product_id))

            if product_tmpl_id:
                domain.append(('product_tmpl_id', '=', product_tmpl_id))

            boms = self.env['mrp.bom'].search(
                domain,
                limit=limit,
                offset=offset,
                order='id'
            )

            results = []
            for bom in boms:
                components = []
                for line in bom.bom_line_ids:
                    components.append({
                        'product_id': line.product_id.id,
                        'product_name': line.product_id.display_name,
                        'quantity': line.product_qty,
                        'uom': line.product_uom_id.name if line.product_uom_id else None,
                    })

                bom_data = {
                    'bom_id': bom.id,
                    'bom_code': bom.code or None,
                    'product_tmpl_id': bom.product_tmpl_id.id if bom.product_tmpl_id else None,
                    'product_tmpl_name': bom.product_tmpl_id.name if bom.product_tmpl_id else None,
                    'product_name': bom.product_id.display_name if bom.product_id else (
                        bom.product_tmpl_id.name if bom.product_tmpl_id else None
                    ),
                    'product_qty': bom.product_qty,
                    'uom': bom.product_uom_id.name if bom.product_uom_id else None,
                    'type': bom.type,
                    'components': components,
                }

                if bom.product_id:
                    bom_data['product_id'] = bom.product_id.id

                results.append(bom_data)

            return results
        except Exception as e:
            _logger.error(f'Error getting BoM list: {str(e)}')
            raise
