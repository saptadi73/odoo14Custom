from odoo import models, fields, api


class ReportSetoranLine(models.Model):
    _name = 'report.setoran.line'
    _auto = False
    _description = 'Report Setoran Line'

    kode_peternak = fields.Char(related='peternak_id.kode_peternak', string='Kode Peternak')
    peternak_id = fields.Many2one('peternak.sapi', 'Peternak')
    liter_sapi_id = fields.Many2one('liter.sapi', 'Liter Sapi Id')
    tgl_setor = fields.Date('Tanggal Setor')
    tipe_setor_pagi = fields.Selection([
        ('1', 'Pagi'),
        ('2', 'Sore')
    ], 'Tipe Setor', required=False)
    setoran_pagi = fields.Float('Setoran Pagi')
    bj_pagi = fields.Float('BJ Pagi', digits=(1, 4))
    tipe_setor_sore = fields.Selection([
        ('1', 'Pagi'),
        ('2', 'Sore')
    ], 'Tipe Setor', required=False)
    setoran_sore = fields.Float('Setoran Sore')
    bj_sore = fields.Float('BJ Sore', digits=(1, 4))
    uom_id = fields.Many2one('uom.uom', 'Uom')
    note = fields.Char('Note')
    setoran_pagi_l = fields.Float('Setoran Pagi (L)')
    setoran_sore_l = fields.Float('Setoran Sore (L)')
    # petugas_id = fields.Many2one('medical.physician', 'Petugas')
    alkohol_pagi = fields.Selection([
        ('1', 'OK'),
        ('2', 'NOT OK'),
    ], 'Alkohol Pagi')
    organol_pagi = fields.Selection([
        ('1', 'OK'),
        ('2', 'NOT OK'),
    ], 'Organoleptik Pagi')
    alkohol_sore = fields.Selection([
        ('1', 'OK'),
        ('2', 'NOT OK'),
    ], 'Alkohol Sore')
    organol_sore = fields.Selection([
        ('1', 'OK'),
        ('2', 'NOT OK'),
    ], 'Organoleptik Sore')
    periode_id = fields.Many2one('periode.setoran', 'Periode')
    tgl_awal = fields.Date('Tanggal Awal', readonly=False)
    tgl_akhir = fields.Date('Tanggal Akhir', readonly=False)

    @api.model
    def init(self):
        # Drop the existing view if it exists
        self.env.cr.execute("DROP VIEW IF EXISTS report_setoran_line CASCADE")

        # Create a new view with the updated SQL query
        self.env.cr.execute("""
                CREATE OR REPLACE VIEW report_setoran_line AS (
                    SELECT
                        sl.id,
                        sl.liter_sapi_id,
                        ls.peternak_id,
                        ps.kode_peternak,
                        ls.periode_id,
                        ls.tgl_awal,
                        ls.tgl_akhir,
                        sl.tgl_setor,
                        sl.tipe_setor_pagi,
                        sl.setoran_pagi,
                        sl.setoran_pagi_l,
                        sl.alkohol_pagi,
                        sl.organol_pagi,
                        sl.bj_pagi,
                        sl.tipe_setor_sore,
                        sl.setoran_sore,
                        sl.setoran_sore_l,
                        sl.alkohol_sore,
                        sl.organol_sore,
                        sl.bj_sore,
                        sl.uom_id,
                        sl.note
                    FROM
                        setoran_line sl
                    LEFT JOIN liter_sapi ls ON ls.id = sl.liter_sapi_id
                    LEFT JOIN peternak_sapi ps ON sl.peternak_id = ps.id
                    LEFT JOIN periode_setoran ps2 ON ls.periode_id = ps2.id
                    LEFT JOIN uom_uom uu ON sl.uom_id = uu.id
                )
            """)
