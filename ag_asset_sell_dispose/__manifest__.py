# -*- coding: utf-8 -*-
#############################################################################
#
#
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

{
    'name': 'Asset Sell Or Dispose',
    'category': 'Asset',
    'version':'14.0',
    'summary': "Selling or Disposing of Assets",
    'author': 'APPSGATE FZC LLC',
    'depends': ['account','base_accounting_kit'],
    'description':""" 
    
            asset,
            sell,
            dispose,
            asset management,
        """,
    'data': [
        'security/ir.model.access.csv',
        'views/asset_split.xml',
        'views/account_view.xml',
        'wizard/asset_dep_wizard.xml',
        'wizard/asset_sell_view.xml'
    ],
    'demo': [
    ],

    'images':[
        'static/src/img/main-screenshot.png'
    ],

    'license': 'AGPL-3',
    'price':'10',
    'currency':'USD',
    'application': True,
    'installable': True,
    'auto_install': False,
}
