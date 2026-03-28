
from odoo import api, fields, models



class ResCompany(models.Model):
    _inherit = 'res.company'

    is_konsolidasi = fields.Boolean(string='Is Konsolidasi', default=False)
    
    
    
    

