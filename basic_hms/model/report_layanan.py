from odoo import models, fields, api, _
from odoo import tools


class report_layanan(models.Model):
    _name = 'report.layanan'
    _auto = False
    _description = 'Report Layanan'

    source_model = fields.Char('Form Layanan')
    petugas_id = fields.Many2one('medical.physician', string="Petugas")
    tgl_layanan = fields.Datetime('Tanggal Layanan')
    jabatan_id = fields.Many2one('master.jabatan', 'Jabatan')

    def init(self):
        self.env.cr.execute("DROP VIEW IF EXISTS report_layanan")

        self.env.cr.execute("""
               CREATE OR REPLACE VIEW report_layanan AS (
                   SELECT
                       fib.id as id,
                       'form_ib' as source_model,
                       fib.petugas_id,
                       fib.tgl_layanan,
                       fib.jabatan_id
                   FROM form_ib fib
                   UNION ALL
                   SELECT
                       fpotk.id as id,
                       'form_pot_kuku' as source_model,
                       fpotk.petugas_id,
                       fpotk.tgl_layanan,
                       fpotk.jabatan_id
                   FROM form_pot_kuku fpotk
                   UNION ALL
                   SELECT
                       fpeng.id as id,
                       'form_pengobatan' as source_model,
                       fpeng.petugas_id,
                       fpeng.tgl_layanan,
                       fpeng.jabatan_id
                   FROM form_pengobatan fpeng
                   UNION ALL
                   SELECT
                       fabor.id as id,
                       'form_abortus' as source_model,
                       fabor.petugas_id,
                       fabor.tgl_layanan,
                       fabor.jabatan_id
                   FROM form_abortus fabor
                   UNION ALL
                   SELECT
                       fmut.id as id,
                       'form_mutasi' as source_model,
                       fmut.petugas_id,
                       fmut.tgl_layanan,
                       fmut.jabatan_id
                   FROM form_mutasi fmut
                   UNION ALL
                   SELECT
                       fgis.id as id,
                       'form_gis' as source_model,
                       fgis.petugas_id,
                       fgis.tgl_layanan,
                       fgis.jabatan_id
                   FROM form_gis fgis
                   UNION ALL
                   SELECT
                       fmas.id as id,
                       'form_masuk' as source_model,
                       fmas.petugas_id,
                       fmas.tgl_layanan,
                       fmas.jabatan_id
                   FROM form_masuk fmas
                   UNION ALL
                   SELECT
                       fmel.id as id,
                       'form_melahirkan' as source_model,
                       fmel.petugas_id,
                       fmel.tgl_layanan,
                       fmel.jabatan_id
                   FROM form_melahirkan fmel
                   UNION ALL
                   SELECT
                       fganpmlk.id as id,
                       'form_ganti_pmlk' as source_model,
                       fganpmlk.petugas_id,
                       fganpmlk.tgl_layanan,
                       fganpmlk.jabatan_id
                   FROM form_ganti_pmlk fganpmlk
                   UNION ALL
                   SELECT
                       fvaksin.id as id,
                       'form_vaksinasi' as source_model,
                       fvaksin.petugas_id,
                       fvaksin.tgl_layanan,
                       fvaksin.jabatan_id
                   FROM form_vaksinasi fvaksin
                   UNION ALL
                   SELECT
                       fspec.id as id,
                       'form_specimen' as source_model,
                       fspec.petugas_id,
                       fspec.tgl_layanan,
                       fspec.jabatan_id
                   FROM form_specimen fspec
                   UNION ALL
                   SELECT
                       fkk.id as id,
                       'form_kk' as source_model,
                       fkk.petugas_id,
                       fkk.tgl_layanan,
                       fkk.jabatan_id
                   FROM form_kk fkk
                   UNION ALL
                   SELECT
                       fnkt.id as id,
                       'form_nkt' as source_model,
                       fnkt.petugas_id,
                       fnkt.tgl_layanan,
                       fnkt.jabatan_id
                   FROM form_nkt fnkt
                   UNION ALL
                   SELECT
                       fpkb.id as id,
                       'form_pkb' as source_model,
                       fpkb.petugas_id,
                       fpkb.tgl_layanan,
                       fpkb.jabatan_id
                   FROM form_pkb fpkb
                   UNION ALL
                   SELECT
                       fpott.id as id,
                       'form_pt' as source_model,
                       fpott.petugas_id,
                       fpott.tgl_layanan,
                       fpott.jabatan_id
                   FROM form_pt fpott
               )
           """)
