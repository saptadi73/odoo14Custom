from odoo import models, fields, api, _
from odoo import tools

class report_transport(models.Model):
    _name = 'report.transport'
    _auto = False
    _description = 'Report Transport'

    responsible = fields.Many2one('res.users', string="Responsible", default=lambda self: self.env.user.id)
    rate_per_km = fields.Float('Tarif')
    distance = fields.Integer('Berat')
    shipment_date = fields.Date('Pickup Date')
    partner_id = fields.Many2one('res.partner', 'Customer')
    product_id = fields.Many2one('product.product', 'Produk')
    route_id = fields.Many2one('transport.route', string="Transport Route")
    source_location_id = fields.Many2one('transport.location', 'Sumber Lokasi')
    destination_location_id = fields.Many2one('transport.location', 'Tujuan Lokasi')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    driver_id = fields.Many2one('res.partner', domain=[('is_driver', '=', True)], string="Driver")
    total_cost = fields.Float(string="Total Cost", tracking=True)
    no_do = fields.Char('No DO')

    @api.model
    def init(self):
        # Drop the existing view if it exists
        # self.env.cr.execute("DROP VIEW IF EXISTS report_transport")

        # Create a new view with the updated SQL query
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW report_transport AS (
                
                SELECT
                    tol.id,
                    ts.responsible,
                    tol.product_id,
                    tol.partner_id,
                    tol.vehicle_id,
                    tol.driver_id,
                    tol.route_id,
                    tol.source_location_id,
                    tol.destination_location_id,
                    tol.rate_per_km,
                    tol.distance,
                    tol.total_cost,
                    tol.shipment_date,
                    ts.status,
                    tol.no_do
                FROM 
                    transport_order_line tol
                    LEFT JOIN transport_shipment ts ON ts.id = tol.transport_line_id
                    LEFT JOIN product_product pp ON tol.product_id = pp.id
                    LEFT JOIN res_users ru ON ts.responsible = ru.id
                    LEFT JOIN res_partner rp ON tol.partner_id = rp.id
                    LEFT JOIN fleet_vehicle fv ON tol.vehicle_id = fv.id
                    LEFT JOIN transport_route tr ON tol.route_id = tr.id
                    LEFT JOIN transport_location tl ON tol.source_location_id = tl.id
            ) 
        """)