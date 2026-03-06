import json
from datetime import datetime, timedelta

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

    def _json_http_response(self, payload, status=200):
        return request.make_response(
            json.dumps(payload),
            headers=[("Content-Type", "application/json; charset=utf-8")],
            status=status,
        )

    def _build_report_domain(self, payload):
        payload = payload or {}
        domain = []

        equipment_code = payload.get("equipment_code")
        if equipment_code:
            domain.append(("equipment_code.equipment_code", "=", str(equipment_code)))

        date_from = payload.get("date_from")
        if date_from:
            domain.append(("date", ">=", fields.Datetime.to_string(self._normalize_datetime(date_from))))

        date_to = payload.get("date_to")
        if date_to:
            domain.append(("date", "<=", fields.Datetime.to_string(self._normalize_datetime(date_to))))

        return domain

    def _get_payload_from_http(self, **kwargs):
        params = request.httprequest.args
        payload = {}
        for key in ("equipment_code", "date_from", "date_to", "interval", "limit", "offset"):
            value = params.get(key)
            if value not in (None, ""):
                payload[key] = value
        payload.update({k: v for k, v in kwargs.items() if v not in (None, "")})
        return payload

    def _get_default_date_range(self):
        now_dt = fields.Datetime.now()
        return now_dt - timedelta(days=30), now_dt

    def _prepare_kpi_response(self, payload):
        Report = request.env["scada.failure.report"]
        domain = self._build_report_domain(payload)

        total_failures = Report.search_count(domain)
        grouped_equipment = Report.read_group(domain, ["equipment_code"], ["equipment_code"], lazy=False)
        unique_equipment = len(grouped_equipment)

        latest = Report.search(domain, order="date desc, id desc", limit=1)
        top_group = sorted(
            grouped_equipment,
            key=lambda item: item.get("equipment_code_count", item.get("__count", 0)),
            reverse=True,
        )
        top_equipment = top_group[0] if top_group else None
        top_equipment_name = ""
        top_equipment_code = ""
        top_equipment_count = 0
        if top_equipment and top_equipment.get("equipment_code"):
            equipment = request.env["scada.equipment"].browse(top_equipment["equipment_code"][0])
            top_equipment_name = equipment.name or ""
            top_equipment_code = equipment.equipment_code or ""
            top_equipment_count = top_equipment.get("equipment_code_count", top_equipment.get("__count", 0))

        return {
            "status": "success",
            "data": {
                "filters": {
                    "equipment_code": payload.get("equipment_code") or None,
                    "date_from": payload.get("date_from") or None,
                    "date_to": payload.get("date_to") or None,
                },
                "kpis": {
                    "total_failures": total_failures,
                    "unique_equipment": unique_equipment,
                    "latest_failure_at": fields.Datetime.to_string(latest.date) if latest else None,
                    "top_equipment": {
                        "equipment_code": top_equipment_code or None,
                        "equipment_name": top_equipment_name or None,
                        "failure_count": top_equipment_count,
                    },
                },
            },
        }

    def _prepare_by_equipment_response(self, payload):
        Report = request.env["scada.failure.report"]
        domain = self._build_report_domain(payload)
        limit = int(payload.get("limit") or 10)
        groups = Report.read_group(domain, ["equipment_code"], ["equipment_code"], lazy=False)
        groups = sorted(
            groups,
            key=lambda item: item.get("equipment_code_count", item.get("__count", 0)),
            reverse=True,
        )[:limit]

        categories = []
        series_data = []
        rows = []
        for group in groups:
            equipment_id = group["equipment_code"] and group["equipment_code"][0]
            equipment = request.env["scada.equipment"].browse(equipment_id) if equipment_id else request.env["scada.equipment"]
            label = equipment.equipment_code or group["equipment_code"][1]
            count = group.get("equipment_code_count", group.get("__count", 0))
            categories.append(label)
            series_data.append(count)
            rows.append({
                "equipment_id": equipment.id if equipment else None,
                "equipment_code": equipment.equipment_code if equipment else None,
                "equipment_name": equipment.name if equipment else group["equipment_code"][1],
                "failure_count": count,
            })

        return {
            "status": "success",
            "data": {
                "filters": {
                    "equipment_code": payload.get("equipment_code") or None,
                    "date_from": payload.get("date_from") or None,
                    "date_to": payload.get("date_to") or None,
                    "limit": limit,
                },
                "chart": {
                    "type": "bar",
                    "categories": categories,
                    "series": [
                        {
                            "name": "Failure Count",
                            "data": series_data,
                        }
                    ],
                },
                "rows": rows,
            },
        }

    def _prepare_timeline_response(self, payload):
        Report = request.env["scada.failure.report"]
        domain = self._build_report_domain(payload)
        interval = (payload.get("interval") or "day").lower()
        if interval not in ("day", "month"):
            return {
                "status": "error",
                "message": "interval must be either 'day' or 'month'",
            }

        group_key = "date:%s" % interval
        groups = Report.read_group(domain, ["date"], [group_key], lazy=False)
        groups = sorted(groups, key=lambda item: item.get(group_key) or "")

        categories = []
        series_data = []
        for group in groups:
            label = group.get(group_key)
            categories.append(str(label) if label is not None else "")
            series_data.append(group["__count"])

        return {
            "status": "success",
            "data": {
                "filters": {
                    "equipment_code": payload.get("equipment_code") or None,
                    "date_from": payload.get("date_from") or None,
                    "date_to": payload.get("date_to") or None,
                    "interval": interval,
                },
                "chart": {
                    "type": "line",
                    "categories": categories,
                    "series": [
                        {
                            "name": "Failure Count",
                            "data": series_data,
                        }
                    ],
                },
            },
        }

    def _prepare_recent_list_response(self, payload):
        Report = request.env["scada.failure.report"]
        domain = self._build_report_domain(payload)
        limit = int(payload.get("limit") or 20)
        offset = int(payload.get("offset") or 0)
        total = Report.search_count(domain)
        records = Report.search(domain, order="date desc, id desc", limit=limit, offset=offset)

        items = []
        for report in records:
            items.append({
                "id": report.id,
                "equipment_id": report.equipment_code.id,
                "equipment_code": report.equipment_code.equipment_code,
                "equipment_name": report.equipment_code.name,
                "description": report.description,
                "date": fields.Datetime.to_string(report.date),
            })

        return {
            "status": "success",
            "data": {
                "filters": {
                    "equipment_code": payload.get("equipment_code") or None,
                    "date_from": payload.get("date_from") or None,
                    "date_to": payload.get("date_to") or None,
                    "limit": limit,
                    "offset": offset,
                },
                "total": total,
                "items": items,
            },
        }

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

    @http.route('/api/scada/failure-report/report/kpi', type='json', auth='user', methods=['POST'])
    def get_failure_report_kpi_json(self, **kwargs):
        payload = self._extract_payload()
        return self._prepare_kpi_response(payload)

    @http.route('/api/scada/failure-report/report/by-equipment', type='json', auth='user', methods=['POST'])
    def get_failure_report_by_equipment_json(self, **kwargs):
        payload = self._extract_payload()
        return self._prepare_by_equipment_response(payload)

    @http.route('/api/scada/failure-report/report/timeline', type='json', auth='user', methods=['POST'])
    def get_failure_report_timeline_json(self, **kwargs):
        payload = self._extract_payload()
        return self._prepare_timeline_response(payload)

    @http.route('/api/scada/failure-report/report/recent', type='json', auth='user', methods=['POST'])
    def get_failure_report_recent_json(self, **kwargs):
        payload = self._extract_payload()
        return self._prepare_recent_list_response(payload)

    @http.route('/api/scada/failure-report/report/kpi', type='http', auth='user', methods=['GET'])
    def get_failure_report_kpi_http(self, **kwargs):
        payload = self._get_payload_from_http(**kwargs)
        return self._json_http_response(self._prepare_kpi_response(payload))

    @http.route('/api/scada/failure-report/report/by-equipment', type='http', auth='user', methods=['GET'])
    def get_failure_report_by_equipment_http(self, **kwargs):
        payload = self._get_payload_from_http(**kwargs)
        return self._json_http_response(self._prepare_by_equipment_response(payload))

    @http.route('/api/scada/failure-report/report/timeline', type='http', auth='user', methods=['GET'])
    def get_failure_report_timeline_http(self, **kwargs):
        payload = self._get_payload_from_http(**kwargs)
        return self._json_http_response(self._prepare_timeline_response(payload))

    @http.route('/api/scada/failure-report/report/recent', type='http', auth='user', methods=['GET'])
    def get_failure_report_recent_http(self, **kwargs):
        payload = self._get_payload_from_http(**kwargs)
        return self._json_http_response(self._prepare_recent_list_response(payload))

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
