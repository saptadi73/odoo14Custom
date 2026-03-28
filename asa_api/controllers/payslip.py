# -*- coding: utf-8 -*-
import json
import logging
import functools
import werkzeug.wrappers

from odoo import http
from odoo.addons.asa_api.models.common import invalid_response, valid_response
from odoo.exceptions import AccessDenied, AccessError
from odoo.http import request
from odoo.addons.asa_api.controllers.controllers import validate_token
from datetime import datetime, timedelta, date

_logger = logging.getLogger(__name__)


class SapiApi(http.Controller):

	@http.route('/get_data_payslip', auth="none", type='json',cors='*')
	def get_payslip(self, **rec):
		try:
			print ("============payslip===========")
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('user_id') :
						print ("============User===========", rec.get('user_id'))
						user = int(rec.get('user_id'))
						employee = request.env['hr.employee'].sudo().search([('user_id','=',user)])
						if len(employee) > 1 :
							return ({'message':'Data Employee lebih dari satu untuk user id yang dicari','user_id': rec.get('user_id')})
						
						elif len(employee) == 1:
							payslip = request.env['hr.payslip'].sudo().search([('employee_id','=',employee.id),('state','=','done')])
							print ("=============payslip===========", payslip)
							pay_slip = []
							for slip in payslip:
								data_slip = { 	'id'        : slip.id,
												'periode_setoran': slip.periode_id.periode_setoran or None,
												'start_date' : slip.periode_id.periode_setoran_awal or None,
												'end_date' : slip.periode_id.periode_setoran_akhir or None,
												# 'total_setoran'	: slip.tot_setoran or None,
												# 'total_harga': slip.total_harga_susu or None
												   
												  }
					
								pay_slip.append(data_slip)
							return ({"message": "List data Payslip", "Payslip List": pay_slip})
						else :
							return ({'message':'Employee tidak ditemukan','user_id': rec.get('user_id')})

					return ({'result':'Failed Check Your Parameter'})

				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}

	@http.route('/select_payslip', auth="none", type='json',cors='*')
	def select_payslip(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('payslip_id') :
						id_slip = int(rec.get('payslip_id'))
						slip = request.env['hr.payslip'].sudo().search([('id','=',id_slip)])
						if slip :
							gross = request.env['hr.payslip.line'].sudo().search([('slip_id','=',slip.id),('code','=','GROSS')],limit=1)
							wajib = request.env['hr.payslip.line'].sudo().search([('slip_id','=',slip.id),('code','=','SIWA')],limit=1)
							sukarela = request.env['hr.payslip.line'].sudo().search([('slip_id','=',slip.id),('code','=','SISU')],limit=1)
							hari_raya = request.env['hr.payslip.line'].sudo().search([('slip_id','=',slip.id),('code','=','SIHR')],limit=1)
							net = request.env['hr.payslip.line'].sudo().search([('slip_id','=',slip.id),('code','=','NET')],limit=1)

							data_slip = { 	'id'        		: slip.id,
											'periode_setoran'	: slip.periode_id.periode_setoran or None,
											'start_date' 		: slip.periode_id.periode_setoran_awal or None,
											'end_date' 			: slip.periode_id.periode_setoran_akhir or None,
											'wilayah'			: slip.liter_id.tps_id.tps_name or None,
											'no_id'				: slip.liter_id.kode_peternak or None,
											'nama_peternak'		: slip.liter_id.peternak_id.peternak_name or None,
											'setor_pagi'		: slip.setor_pagi or 0.0,
											'setor_sore'		: slip.setor_sore or 0.0,
											'total_liter'		: slip.tot_setoran or 0.0,
											'bj'				: slip.liter_id.avg_setor or 0.0,
											# 'fat'				: slip.fat or 0.0,
											# 'grade'				: slip.grade or 0.0,
											'harga_kualitas'	: slip.harga_kual or 0.0,
											'premi_produksi'	: slip.insen_prod or 0.0,
											'premi_efisiensi'	: slip.insen_pmk or 0.0,
											'harga_satuan'		: slip.harga_satuan or 0.0,
											'allowance'			: 0.0,
											'gross'				: gross.total or 0.0,
											# 'total_harga'		: slip.total_harga_susu or 0.0,
											'potongan_wajib'	: wajib.total or 0.0,
											'potongan_sukarela'	: sukarela.total or 0.0,
											'potongan_hr'		: hari_raya.total or 0.0,
											'total_terima'		: net.total or 0.0
											   
											  }
							return ({"message": "Detail Payslip", "Detail": data_slip})
						else :
							return ({'message':'Payslip tidak ditemukan','payslip_id': rec.get('payslip_id')})

					return ({'result':'Failed Check Your Parameter'})

				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}


	@http.route('/get_setoran_susu', auth="none", type='json',cors='*')
	def get_setoran(self, **rec):
		try:
			header = request.httprequest.headers
			db= header.get('db')
			login = header.get('login')
			password = header.get('password')
			uid = request.session.authenticate(db, login, password)
			if uid:
				if request.jsonrequest :
					if rec.get('peternak_id') :
						peternak = int(rec.get('peternak_id'))
						start_date = rec.get('start_date')+' 00:00:00'
						end_date = rec.get('start_end')+ ' 23:59:59'
						setoran = request.env['setoran.line'].search([('peternak_id','=',peternak),('tgl_setor','>=',start_date),
																		('tgl_setor','<=',end_date)])

						if setoran :
							liter = []
							tgl = False
							for s in setoran:
								setor = request.env['setoran.line'].search([('peternak_id','=',peternak),('tgl_setor','>=',start_date),
																		('tgl_setor','<=',end_date)])
		
								pagi_setor = 0
								sore_setor = 0
								pagi_bj = 0
								sore_bj = 0
								for p in setor:
									if p.tgl_setor == s.tgl_setor :
										if p.tipe_setor_pagi == '1' :
											pagi_setor = p.setoran_pagi
											pagi_bj = p.bj
										elif p.tipe_setor_pagi == '2' :
											sore_setor = p.setoran_sore
											sore_bj = p.bj
										else :
											pagi_setor =0
											sore_setor =0
											pagi_bj = 0
											sore_bj = 0

								if tgl != s.tgl_setor :
									data = { 	'id'        : s.id,
												'wilayah': s.tps_id.tps_name or None,
												'date' : s.tgl_setor or None,
												'pagi' : pagi_setor or 0.0,
												'sore' : sore_setor or 0.0,
												'jumlah' : pagi_setor + sore_setor or 0.0,
												'bj_pagi' : pagi_bj or 0.0,
												'bj_sore' : sore_bj or 0.0,
													   
													  }
							
									liter.append(data)
								tgl = s.tgl_setor
							return ({"message": "List data Setoran", "Data": liter})
						else :
							return ({'message':'Belum ada Setoran','peternak_id': rec.get('peternak_id')})

					return ({'result':'Failed Check Your Parameter'})

				return ({'result':'Failed Check Your Parameter'})
		except Exception as e:
			return {'status': False, 'error': str(e)}

		
