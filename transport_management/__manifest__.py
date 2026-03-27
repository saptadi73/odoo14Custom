# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
{
    'name': "Sales Transport Management | Shipping Management | Freight Management | Transport Management | Courier Management",
    'summary': """
        Sales Transport Management, Shipment Management & Freight Management
    """,
    'description': """
       - Sales Transport Management
       - Sales Shipping Management
       - Transport Management
       - Freight Management
       - Delivery Order Management
       - Courier Management
    """,
    'category': 'Sales/Sales',
    'version': '14.0.0.0',
    'author': 'TechKhedut Inc.',
    'company': 'TechKhedut Inc.',
    'maintainer': 'TechKhedut Inc.',
    'website': "https://www.techkhedut.com",
    'depends': [
        'mail',
        'contacts',
        'fleet',
        'sale_management',
        'sale',
    ],
    'data':[
        # Data
        'data/sequence.xml',
        'data/data.xml',
        # Security
        'security/ir.model.access.csv',
        # Wizard
        'wizard/ship_order_views.xml',
        'wizard/shipment_reschedule.xml',
        # Views
        'views/transporter_views.xml',
        'views/delivery_type_views.xml',
        'views/transport_location_views.xml',
        'views/transport_route_views.xml',
        'views/fleet_vehicle_views.xml',
        'views/res_partner_views.xml',
        'views/shipment_operation_views.xml',
        'views/transport_shipment_views.xml',
        'views/stock_picking_views.xml',
        'views/transport_delivery_order_views.xml',
        'views/sale_order.xml',
        # Reports
        'report/delivery_order.xml',
        # Templates
        'views/assets.xml',
        # Groups
        'security/groups.xml',
        # Menu
        'views/menus.xml',
        # Report
        'views/report_transport_views.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml'
    ],
    'images': ['static/description/shipment-management.gif'],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 99.0,
    'currency': 'USD',
}
