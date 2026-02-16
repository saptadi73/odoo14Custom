from datetime import datetime

from odoo import fields, http
from odoo.http import request


class ScadaFailureReportController(http.Controller):

    def _extract_payload(self):
        payload = request.jsonrequest or {}
        if isinstance(payload, dict) and isinstance(payload.get('params'), dict):
            return payload['params']
        return payload if isinstance(payload, dict) else {}

    def _normalize_datetime(self, value):
        if not value:
            return fields.Datetime.now()
        if isinstance(value, datetime):
            return value

        cleaned = str(value).strip().replace('T', ' ')
        # Support format from HTML datetime-local without seconds.
        if len(cleaned) == 16:
            cleaned = f"{cleaned}:00"
        return fields.Datetime.to_datetime(cleaned)

    def _create_failure_report(self, equipment_code_value, description, date_value):
        if not equipment_code_value:
            return {'status': 'error', 'message': 'equipment_code is required'}
        if not description:
            return {'status': 'error', 'message': 'description is required'}

        equipment = request.env['scada.equipment'].search([
            ('equipment_code', '=', equipment_code_value),
        ], limit=1)
        if not equipment:
            return {
                'status': 'error',
                'message': f'Equipment with code "{equipment_code_value}" not found',
            }

        try:
            report_date = self._normalize_datetime(date_value)
        except Exception:
            return {
                'status': 'error',
                'message': 'Invalid date format. Use YYYY-MM-DD HH:MM:SS or YYYY-MM-DDTHH:MM',
            }

        report = request.env['scada.failure.report'].create({
            'equipment_code': equipment.id,
            'description': description,
            'date': fields.Datetime.to_string(report_date),
        })
        return {
            'status': 'success',
            'message': 'Failure report created',
            'data': {
                'id': report.id,
                'equipment_code': equipment.equipment_code,
                'description': report.description,
                'date': fields.Datetime.to_string(report.date),
            },
        }

    @http.route('/api/scada/failure-report', type='json', auth='user', methods=['POST'])
    def create_failure_report(self, **kwargs):
        payload = self._extract_payload()
        return self._create_failure_report(
            payload.get('equipment_code'),
            payload.get('description'),
            payload.get('date'),
        )

    @http.route('/scada/failure-report/input', type='http', auth='user', methods=['GET'])
    def failure_report_input_form(self, **kwargs):
        equipment_list = request.env['scada.equipment'].search([], order='name asc')
        options_html = ''.join(
            f'<option value="{eq.equipment_code}">{eq.equipment_code} - {eq.name}</option>'
            for eq in equipment_list
        )
        html = f"""
<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <title>SCADA Failure Report Input</title>
</head>
<body>
  <h2>Input SCADA Failure Report</h2>
  <form action=\"/scada/failure-report/submit\" method=\"post\">
    <input type=\"hidden\" name=\"csrf_token\" value=\"{request.csrf_token()}\" />
    <label>Equipment Code</label><br/>
    <select name=\"equipment_code\" required>
      <option value=\"\">-- Select Equipment --</option>
      {options_html}
    </select><br/><br/>

    <label>Description</label><br/>
    <textarea name=\"description\" rows=\"5\" cols=\"60\" required></textarea><br/><br/>

    <label>Date</label><br/>
    <input type=\"datetime-local\" name=\"date\" /><br/><br/>

    <button type=\"submit\">Submit</button>
  </form>
</body>
</html>
"""
        return request.make_response(html)

    @http.route('/scada/failure-report/submit', type='http', auth='user', methods=['POST'])
    def submit_failure_report_form(self, **post):
        result = self._create_failure_report(
            post.get('equipment_code'),
            post.get('description'),
            post.get('date'),
        )

        if result.get('status') == 'success':
            body = (
                '<h3>Failure report berhasil disimpan.</h3>'
                '<p><a href="/scada/failure-report/input">Input lagi</a></p>'
            )
        else:
            body = (
                f"<h3>Gagal menyimpan: {result.get('message')}</h3>"
                '<p><a href="/scada/failure-report/input">Kembali ke form</a></p>'
            )

        return request.make_response(
            f"<!doctype html><html><body>{body}</body></html>",
            headers=[('Content-Type', 'text/html; charset=utf-8')],
        )
