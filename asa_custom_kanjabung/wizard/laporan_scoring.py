# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools import pycompat


class ScoringReportWizard(models.TransientModel):
    _name = 'scoring.report.wizard'
    _description = 'Scoring Report Wizard'


    periode_ids = fields.Many2many(
        comodel_name='periode.setoran',
        string='Periode',
        required=True,
    )
    peternak_ids = fields.Many2many(
        comodel_name='peternak.sapi',
        string='Nama Anggota',
        required=True,
    )
    monthly = fields.Boolean('Monthly')

    def calculte_data(self):
        for res in self:
            self.ensure_one()
            
            if self.peternak_ids :
                for pr in self.periode_ids :
                    for p in self.peternak_ids :
                        self._cr.execute(
                        """
                            WITH anggota AS (SELECT s.periode_id,s.peternak_id,s.mpak,s.tanggal_kunjungan FROM form_kunjungan_gdfp s 
                            WHERE s.jenis_management = '1' and s.periode_id = %s
                            ORDER BY s.tanggal_kunjungan desc)
                            SELECT a.periode_id,a.peternak_id,a.mpak FROM anggota a 
                            WHERE a.peternak_id = %s
                            ORDER BY a.tanggal_kunjungan desc limit 1
                        """,
                        (
                            pr.id,
                            p.id
                        ),
                        )
                        dd_data = self._cr.dictfetchall()
                        print ("=============data pakan==========", dd_data)
                        ReportLine = self.env["scoring.report.view"] 
 
                        for d in dd_data :
                            data = {
                                        'periode_id': d['periode_id'],
                                        'kode_anggota': self.env['peternak.sapi'].browse(d['peternak_id']).kode_peternak,
                                        'peternak_id':d['peternak_id'],
                                        'pakan': d['mpak'] or 0,
                                        'kandang': 0,
                                        'pemerahan': 0,
                                        'bisnis': 0,
                                        'limbah': 0,
                                        'kesehatan': 0
                                    }

                            ReportLine.create(data)

                for pr in self.periode_ids :
                    for p in self.peternak_ids :
                        self._cr.execute(
                        """
                            WITH anggota AS (SELECT s.periode_id,s.peternak_id,s.mkan,s.tanggal_kunjungan FROM form_kunjungan_gdfp s 
                            WHERE s.jenis_management = '2' and s.periode_id = %s
                            ORDER BY s.tanggal_kunjungan desc)
                            SELECT a.periode_id,a.peternak_id,a.mkan FROM anggota a 
                            WHERE a.peternak_id = %s
                            ORDER BY a.tanggal_kunjungan desc limit 1
                        """,
                        (
                            pr.id,
                            p.id
                        ),
                        )
                        dd_data = self._cr.dictfetchall()
                        ReportLine = self.env["scoring.report.view"] 
 
                        for d in dd_data :
                            data = {
                                        'periode_id': d['periode_id'],
                                        'kode_anggota': self.env['peternak.sapi'].browse(d['peternak_id']).kode_peternak,
                                        'peternak_id':d['peternak_id'],
                                        'pakan':  0,
                                        'kandang': d['mkan'] or 0,
                                        'pemerahan': 0,
                                        'bisnis': 0,
                                        'limbah': 0,
                                        'kesehatan': 0
                                    }

                            ReportLine.create(data)

                for pr in self.periode_ids :
                    for p in self.peternak_ids :
                        self._cr.execute(
                        """
                            WITH anggota AS (SELECT s.periode_id,s.peternak_id,s.mpem,s.tanggal_kunjungan FROM form_kunjungan_gdfp s 
                            WHERE s.jenis_management = '3' and s.periode_id = %s
                            ORDER BY s.tanggal_kunjungan desc)
                            SELECT a.periode_id,a.peternak_id,a.mpem FROM anggota a 
                            WHERE a.peternak_id = %s
                            ORDER BY a.tanggal_kunjungan desc limit 1
                        """,
                        (
                            pr.id,
                            p.id
                        ),
                        )
                        dd_data = self._cr.dictfetchall()
                        ReportLine = self.env["scoring.report.view"] 
 
                        for d in dd_data :
                            data = {
                                        'periode_id': d['periode_id'],
                                        'kode_anggota': self.env['peternak.sapi'].browse(d['peternak_id']).kode_peternak,
                                        'peternak_id':d['peternak_id'],
                                        'pakan':  0,
                                        'kandang': 0,
                                        'pemerahan': d['mpem'] or 0,
                                        'bisnis': 0,
                                        'limbah': 0,
                                        'kesehatan': 0
                                    }

                            ReportLine.create(data)

                for pr in self.periode_ids :
                    for p in self.peternak_ids :
                        self._cr.execute(
                        """
                            WITH anggota AS (SELECT s.periode_id,s.peternak_id,s.mbis,s.tanggal_kunjungan FROM form_kunjungan_gdfp s 
                            WHERE s.jenis_management = '4' and s.periode_id = %s
                            ORDER BY s.tanggal_kunjungan desc)
                            SELECT a.periode_id,a.peternak_id,a.mbis FROM anggota a 
                            WHERE a.peternak_id = %s
                            ORDER BY a.tanggal_kunjungan desc limit 1
                        """,
                        (
                            pr.id,
                            p.id
                        ),
                        )
                        dd_data = self._cr.dictfetchall()
                        ReportLine = self.env["scoring.report.view"] 
 
                        for d in dd_data :
                            data = {
                                        'periode_id': d['periode_id'],
                                        'kode_anggota': self.env['peternak.sapi'].browse(d['peternak_id']).kode_peternak,
                                        'peternak_id':d['peternak_id'],
                                        'pakan':  0,
                                        'kandang': 0,
                                        'pemerahan': 0,
                                        'bisnis': d['mbis'] or 0,
                                        'limbah': 0,
                                        'kesehatan': 0
                                    }

                            ReportLine.create(data)


                for pr in self.periode_ids :
                    for p in self.peternak_ids :
                        self._cr.execute(
                        """
                            WITH anggota AS (SELECT s.periode_id,s.peternak_id,s.mpel,s.tanggal_kunjungan FROM form_kunjungan_gdfp s 
                            WHERE s.jenis_management = '5' and s.periode_id = %s
                            ORDER BY s.tanggal_kunjungan desc)
                            SELECT a.periode_id,a.peternak_id,a.mpel FROM anggota a 
                            WHERE a.peternak_id = %s
                            ORDER BY a.tanggal_kunjungan desc limit 1
                        """,
                        (
                            pr.id,
                            p.id
                        ),
                        )
                        dd_data = self._cr.dictfetchall()
                        ReportLine = self.env["scoring.report.view"] 
 
                        for d in dd_data :
                            data = {
                                        'periode_id': d['periode_id'],
                                        'kode_anggota': self.env['peternak.sapi'].browse(d['peternak_id']).kode_peternak,
                                        'peternak_id':d['peternak_id'],
                                        'pakan':  0,
                                        'kandang': 0,
                                        'pemerahan': 0,
                                        'bisnis': 0,
                                        'limbah': d['mpel'] or 0,
                                        'kesehatan': 0
                                    }

                            ReportLine.create(data)

                for pr in self.periode_ids :
                    for p in self.peternak_ids :
                        self._cr.execute(
                        """
                            SELECT p.periode_id,p.peternak_id, sum(p.bcs) as bcs FROM form_pengobatan p 
                            WHERE p.periode_id = %s and p.peternak_id = %s
                            GROUP BY p.periode_id,p.peternak_id
                            ORDER BY p.periode_id desc
                        """,
                        (
                            pr.id,
                            p.id
                        ),
                        )
                        p_data = self._cr.dictfetchall()
                        a = 0
                        for rec in p_data :
                            a = rec['bcs']

                        self._cr.execute(
                        """
                            SELECT a.periode_id,a.peternak_id, sum(a.bcs) as bcs FROM form_abortus a 
                            WHERE a.periode_id = %s and a.peternak_id = %s
                            GROUP BY a.periode_id,a.peternak_id
                            ORDER BY a.periode_id desc
                        """,
                        (
                            pr.id,
                            p.id
                        ),
                        )
                        a_data = self._cr.dictfetchall()
                        b = 0
                        for rec in a_data :
                            b = rec['bcs']

                        self._cr.execute(
                        """
                            SELECT p.periode_id,p.peternak_id, sum(p.bcs) as bcs FROM form_pkb p 
                            WHERE p.periode_id = %s and p.peternak_id = %s
                            GROUP BY p.periode_id,p.peternak_id
                            ORDER BY p.periode_id desc
                        """,
                        (
                            pr.id,
                            p.id
                        ),
                        )
                        p_data = self._cr.dictfetchall()
                        c = 0
                        for rec in p_data :
                            c = rec['bcs']

                        self._cr.execute(
                        """
                            SELECT m.periode_id,m.peternak_id, sum(m.bcs) as bcs FROM form_mutasi m 
                            WHERE m.periode_id = %s and m.peternak_id = %s
                            GROUP BY m.periode_id,m.peternak_id
                            ORDER BY m.periode_id desc
                        """,
                        (
                            pr.id,
                            p.id
                        ),
                        )
                        m_data = self._cr.dictfetchall()
                        d = 0
                        for rec in m_data :
                            d = rec['bcs']

                        self._cr.execute(
                        """
                            SELECT g.periode_id,g.peternak_id, sum(g.bcs) as bcs FROM form_gis g 
                            WHERE g.periode_id = %s and g.peternak_id = %s
                            GROUP BY g.periode_id,g.peternak_id
                            ORDER BY g.periode_id desc
                        """,
                        (
                            pr.id,
                            p.id
                        ),
                        )
                        g_data = self._cr.dictfetchall()
                        e = 0
                        for rec in g_data :
                            e = rec['bcs']

                        self._cr.execute(
                        """
                            SELECT i.periode_id,i.peternak_id, sum(i.bcs) as bcs FROM form_ib i 
                            WHERE i.periode_id = %s and i.peternak_id = %s
                            GROUP BY i.periode_id,i.peternak_id
                            ORDER BY i.periode_id desc
                        """,
                        (
                            pr.id,
                            p.id
                        ),
                        )
                        i_data = self._cr.dictfetchall()
                        f = 0
                        for rec in i_data :
                            f = rec['bcs']

                        self._cr.execute(
                        """
                            SELECT k.periode_id,k.peternak_id, sum(k.bcs) as bcs FROM form_kk k 
                            WHERE k.periode_id = %s and k.peternak_id = %s
                            GROUP BY k.periode_id,k.peternak_id
                            ORDER BY k.periode_id desc
                        """,
                        (
                            pr.id,
                            p.id
                        ),
                        )
                        k_data = self._cr.dictfetchall()
                        g = 0
                        for rec in k_data :
                            g = rec['bcs']

                        self._cr.execute(
                        """
                            SELECT ms.periode_id,ms.peternak_id, sum(ms.bcs) as bcs FROM form_masuk ms 
                            WHERE ms.periode_id = %s and ms.peternak_id = %s
                            GROUP BY ms.periode_id,ms.peternak_id
                            ORDER BY ms.periode_id desc
                        """,
                        (
                            pr.id,
                            p.id
                        ),
                        )
                        ms_data = self._cr.dictfetchall()
                        h = 0
                        for rec in ms_data :
                            h = rec['bcs']

                        self._cr.execute(
                        """
                            SELECT ml.periode_id,ml.peternak_id, sum(ml.bcs) as bcs FROM form_melahirkan ml 
                            WHERE ml.periode_id = %s and ml.peternak_id = %s
                            GROUP BY ml.periode_id,ml.peternak_id
                            ORDER BY ml.periode_id desc
                        """,
                        (
                            pr.id,
                            p.id
                        ),
                        )
                        ml_data = self._cr.dictfetchall()
                        i = 0
                        for rec in ml_data :
                            i = rec['bcs']

                        self._cr.execute(
                        """
                            SELECT n.periode_id,n.peternak_id, sum(n.bcs) as bcs FROM form_nkt n 
                            WHERE n.periode_id = %s and n.peternak_id = %s
                            GROUP BY n.periode_id,n.peternak_id
                            ORDER BY n.periode_id desc
                        """,
                        (
                            pr.id,
                            p.id
                        ),
                        )
                        n_data = self._cr.dictfetchall()
                        j = 0
                        for rec in n_data :
                            j = rec['bcs']

                        self._cr.execute(
                        """
                            SELECT pr.periode_id,pr.peternak_id, sum(pr.bcs) as bcs FROM form_pr pr 
                            WHERE pr.periode_id = %s and pr.peternak_id = %s
                            GROUP BY pr.periode_id,pr.peternak_id
                            ORDER BY pr.periode_id desc
                        """,
                        (
                            pr.id,
                            p.id
                        ),
                        )
                        pr_data = self._cr.dictfetchall()
                        k = 0
                        for rec in pr_data :
                            k = rec['bcs']

                        self._cr.execute(
                        """
                            SELECT pt.periode_id,pt.peternak_id, sum(pt.bcs) as bcs FROM form_pt pt 
                            WHERE pt.periode_id = %s and pt.peternak_id = %s
                            GROUP BY pt.periode_id,pt.peternak_id
                            ORDER BY pt.periode_id desc
                        """,
                        (
                            pr.id,
                            p.id
                        ),
                        )
                        pt_data = self._cr.dictfetchall()
                        l = 0
                        for rec in pt_data :
                            l = rec['bcs']

                        self._cr.execute(
                        """
                            SELECT s.periode_id,s.peternak_id, sum(s.bcs) as bcs FROM form_sq s
                            WHERE s.periode_id = %s and s.peternak_id = %s
                            GROUP BY s.periode_id,s.peternak_id
                            ORDER BY s.periode_id desc
                        """,
                        (
                            pr.id,
                            p.id
                        ),
                        )
                        s_data = self._cr.dictfetchall()
                        m = 0
                        for rec in s_data :
                            m = rec['bcs']


                        self._cr.execute(
                        """
                            SELECT sp.periode_id,sp.peternak_id, sum(sp.bcs) as bcs FROM form_specimen sp
                            WHERE sp.periode_id = %s and sp.peternak_id = %s
                            GROUP BY sp.periode_id,sp.peternak_id
                            ORDER BY sp.periode_id desc
                        """,
                        (
                            pr.id,
                            p.id
                        ),
                        )
                        sp_data = self._cr.dictfetchall()
                        n = 0
                        for rec in sp_data :
                            n = rec['bcs']


                        self._cr.execute(
                        """
                            SELECT g.periode_id,g.peternak_baru_id, sum(g.bcs) as bcs FROM form_ganti_pmlk g
                            WHERE g.periode_id = %s and g.peternak_baru_id = %s
                            GROUP BY g.periode_id,g.peternak_baru_id
                            ORDER BY g.periode_id desc
                        """,
                        (
                            pr.id,
                            p.id
                        ),
                        )
                        g_data = self._cr.dictfetchall()
                        o = 0
                        for rec in g_data :
                            o = rec['bcs']


                        self._cr.execute(
                        """
                            SELECT v.periode_id,v.peternak_id, sum(v.bcs) as bcs FROM form_vaksinasi v
                            WHERE v.periode_id = %s and v.peternak_id = %s
                            GROUP BY v.periode_id,v.peternak_id
                            ORDER BY v.periode_id desc
                        """,
                        (
                            pr.id,
                            p.id
                        ),
                        )
                        v_data = self._cr.dictfetchall()
                        pv = 0
                        for rec in v_data :
                            pv = rec['bcs']


                        self._cr.execute(
                        """
                            SELECT pk.periode_id,pk.peternak_id, sum(pk.bcs) as bcs FROM form_pot_kuku pk
                            WHERE pk.periode_id = %s and pk.peternak_id = %s
                            GROUP BY pk.periode_id,pk.peternak_id
                            ORDER BY pk.periode_id desc
                        """,
                        (
                            pr.id,
                            p.id
                        ),
                        )
                        pk_data = self._cr.dictfetchall()
                        q = 0
                        for rec in pk_data :
                            q = rec['bcs']

                        
                        sapi = self.env['sapi'].search_count([('peternak_id', '=', p.id)])

                        total = a+b+c+d+e+f+g+h+i+j+k+l+m+n+o+pv+q

                        print ("===========sum============", sapi,total)
                        ReportLine = self.env["scoring.report.view"] 
                        data = {
                                    'periode_id': pr.id,
                                    'kode_anggota': self.env['peternak.sapi'].browse(p.id).kode_peternak,
                                    'peternak_id':p.id,
                                    'pakan':  0,
                                    'kandang': 0,
                                    'pemerahan': 0,
                                    'bisnis': 0,
                                    'limbah': 0,
                                    'kesehatan': total/sapi
                                }

                        ReportLine.create(data)


    def calculte_data_monthly(self):
        for res in self:
            self.ensure_one()
            if self.peternak_ids and self.periode_ids :


                self._cr.execute(
                """
                    SELECT s.peternak_id,sum(s.pakan) as pakan,sum(s.kandang) as kandang,sum(s.pemerahan) as pemerahan,sum(s.bisnis) as bisnis,sum(s.limbah) as limbah,sum(s.kesehatan) as kesehatan FROM scoring_report_view s 
                    GROUP BY s.peternak_id
                """
                )

                dd_data = self._cr.dictfetchall()
                print ("=============data pakan==========", dd_data)
                ReportLine = self.env["scoring.report.monthly.view"] 

                for d in dd_data :
                    data = {
                                'kode_anggota': self.env['peternak.sapi'].browse(d['peternak_id']).kode_peternak,
                                'peternak_id':d['peternak_id'],
                                'pakan': d['pakan'] or 0,
                                'kandang': d['kandang'] or 0,
                                'pemerahan': d['pemerahan'] or 0,
                                'bisnis': d['bisnis'] or 0,
                                'limbah': d['limbah'] or 0,
                                'kesehatan': d['kesehatan'] or 0,
                                'total_scoring': (d['pakan']+d['kandang']+d['pemerahan']+d['bisnis']+d['limbah']+d['kesehatan'])/len(self.periode_ids)
                            }

                    ReportLine.create(data)




    def button_compute(self):
        self.ensure_one()
        ReportLine = self.env["scoring.report.view"]
        ReportLine_monthly = self.env["scoring.report.monthly.view"]
        ReportLine.search([]).unlink()
        ReportLine_monthly.search([]).unlink()
        self.calculte_data()
        if self.monthly != True :
            return {
                'name': _('Scoring Report'),
                'view_mode': 'tree,pivot',
                'res_model': 'scoring.report.view',
                'view_id': False,
                'context': {},
                'type': 'ir.actions.act_window'
            }  
        else :
            self.calculte_data_monthly()
            return {
                'name': _('Scoring Report Monthly'),
                'view_mode': 'tree,pivot',
                'res_model': 'scoring.report.monthly.view',
                'view_id': False,
                'context': {},
                'type': 'ir.actions.act_window'
            }  





class ScoringReportView(models.TransientModel):
    _name           = "scoring.report.view"
    _rec_name       = 'peternak_id'
    _description    = 'Laporan Persediaan View'

    periode_id      = fields.Many2one('periode.setoran', string="Periode")
    kode_anggota    = fields.Char(string="Kode Anggota")
    peternak_id     = fields.Many2one('peternak.sapi',string='Nama Anggota')
    pakan           = fields.Integer(string="Management Pakan")
    kandang         = fields.Integer(string="Management Kandang")
    pemerahan       = fields.Integer(string="Management Pemerahan")
    bisnis          = fields.Integer(string="Daya Saing Bisnis")
    limbah          = fields.Integer(string="Pengolahan Limbah")
    kesehatan       = fields.Integer(string="Kesehatan Hewan")
    total_scoring   = fields.Integer(string="Total Scoring", compute="_get_total", store=True)
    categ_scoring   = fields.Char(string="Kategori Scoring", compute="_get_total", store=True)


    @api.depends('pakan','kandang','pemerahan','bisnis','limbah','kesehatan')
    def _get_total(self):
        for rec in self:
            total_scoring = rec.pakan+rec.kandang+rec.pemerahan+rec.bisnis+rec.limbah+rec.kesehatan
            rec.total_scoring = total_scoring
            if total_scoring > 85 :
                rec.categ_scoring = 'GRADE A'
            elif total_scoring >= 70 :
                rec.categ_scoring = 'GRADE B'
            elif total_scoring >= 53 :
                rec.categ_scoring = 'GRADE C'
            else :
                rec.categ_scoring = 'GRADE D'


class ScoringReportMonthlyView(models.TransientModel):
    _name           = "scoring.report.monthly.view"
    _rec_name       = 'peternak_id'
    _description    = 'Laporan Persediaan Monthly View'

    kode_anggota    = fields.Char(string="Kode Anggota")
    peternak_id     = fields.Many2one('peternak.sapi',string='Nama Anggota')
    pakan           = fields.Integer(string="Management Pakan")
    kandang         = fields.Integer(string="Management Kandang")
    pemerahan       = fields.Integer(string="Management Pemerahan")
    bisnis          = fields.Integer(string="Daya Saing Bisnis")
    limbah          = fields.Integer(string="Pengolahan Limbah")
    kesehatan       = fields.Integer(string="Kesehatan Hewan")
    total_scoring   = fields.Integer(string="Scoring Rata-rata")
    categ_scoring   = fields.Char(string="Kategori Scoring", compute="_get_total", store=True)


    @api.depends('pakan','kandang','pemerahan','bisnis','limbah','kesehatan')
    def _get_total(self):
        for rec in self:
            total_scoring = rec.total_scoring
            rec.total_scoring = total_scoring
            if total_scoring > 85 :
                rec.categ_scoring = 'GRADE A'
            elif total_scoring >= 70 :
                rec.categ_scoring = 'GRADE B'
            elif total_scoring >= 53 :
                rec.categ_scoring = 'GRADE C'
            else :
                rec.categ_scoring = 'GRADE D'

