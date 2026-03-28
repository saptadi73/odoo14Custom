# -*- coding: utf-8 -*-
#############################################################################
#
#    bispro.vn.
#
#    Copyright (C) 2020 bispro.vn(<http://bispro.vn)
#    Author: bispro.vn (<http://bispro.vn)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

{
    'name': 'BISPRO Partner Filter by Customer or Vendor',
    'version': '14.0.0.0.1',
    'category': 'Accounting',
    'author': 'BISPRO.VN,',
    'website': 'https://bispro.vn',
    'summary': 'BISPRO Partner Filter by Customer or Vendor',
    'images': ["static/description/icon.png"],
    'depends': [
        'account',
        'base',
        'sale',
        'purchase',
    ],
    'data': [
        'views/res_partner_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
