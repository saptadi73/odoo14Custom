"""
Product Service
Business logic untuk mengambil data produk
"""

import logging
from typing import Optional

_logger = logging.getLogger(__name__)


class ProductService:
    """Service untuk data produk"""

    def __init__(self, env):
        self.env = env

    def get_product_list(
        self,
        category_id=None,
        category_name=None,
        limit=100,
        offset=0,
        active: Optional[bool] = True
    ):
        """
        Get list produk dengan filter kategori optional.

        Args:
            category_id: ID kategori (int) atau None
            category_name: Nama kategori (str) atau None
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

            if category_id:
                domain.append(('categ_id', '=', category_id))

            if category_name:
                domain.append(('categ_id.name', 'ilike', category_name))

            products = self.env['product.product'].search_read(
                domain,
                fields=['id', 'name', 'categ_id', 'type', 'product_tmpl_id'],
                limit=limit,
                offset=offset,
                order='name'
            )

            return [
                {
                    'product_id': p['id'],
                    'product_name': p['name'],
                    'product_tmpl_id': p['product_tmpl_id'][0] if p.get('product_tmpl_id') else None,
                    'product_category': p['categ_id'][1] if p.get('categ_id') else None,
                    'product_type': p.get('type'),
                }
                for p in products
            ]
        except Exception as e:
            _logger.error(f'Error getting product list: {str(e)}')
            raise
