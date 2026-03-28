import json
import logging

from odoo import _, fields, http
from odoo.http import request

_logger = logging.getLogger(__name__)


class SalesBusinessCategoryApiController(http.Controller):
    def _get_json_payload(self):
        payload = request.jsonrequest or {}
        if isinstance(payload, dict):
            params = payload.get("params")
            if isinstance(params, dict):
                return params
        return payload

    def _success(self, data=None, message=None):
        response = {"status": "success"}
        if message:
            response["message"] = message
        response["data"] = data or {}
        return response

    def _error(self, message):
        return {"status": "error", "message": message}

    def _authenticate_session(self, login, password, dbname=None):
        db = dbname or request.session.db or request.env.cr.dbname
        uid = request.session.authenticate(db, login, password)
        if not uid:
            return self._error("Invalid credentials")

        user = request.env.user.sudo()
        return self._success(
            {
                "uid": uid,
                "session_id": request.session.sid,
                "db": db,
                "login": user.login,
                "name": user.name,
                "partner_id": user.partner_id.id,
                "company_id": user.company_id.id,
                "company_name": user.company_id.name,
            },
            "Authentication successful",
        )

    def _get_partner_by_qr_ref(self, customer_qr_ref):
        qr_ref = (customer_qr_ref or "").strip()
        if not qr_ref:
            raise ValueError("customer_qr_ref is required")

        partner = request.env["res.partner"].search(
            [("customer_qr_ref", "=", qr_ref), ("parent_id", "=", False)],
            limit=1,
        )
        if not partner:
            raise ValueError(_("Customer with QR reference '%s' was not found.") % qr_ref)
        return partner.commercial_partner_id

    def _get_partner_by_id(self, partner_id):
        partner_id = int(partner_id or 0)
        if not partner_id:
            raise ValueError("customer_id is required")

        partner = request.env["res.partner"].browse(partner_id).exists().commercial_partner_id
        if not partner:
            raise ValueError(_("Customer with id '%s' was not found.") % partner_id)
        return partner

    def _build_customer_qr_payload(self, partner):
        return {
            "customer_id": partner.id,
            "customer_qr_ref": partner.customer_qr_ref,
            "customer_name": partner.name,
        }

    def _build_qr_content(self, qr_payload, qr_format):
        qr_format = (qr_format or "ref").strip().lower()
        if qr_format == "ref":
            return qr_payload["customer_qr_ref"], qr_format
        if qr_format == "json":
            return json.dumps(qr_payload, ensure_ascii=True, separators=(",", ":")), qr_format
        raise ValueError("format must be either 'ref' or 'json'")

    def _get_limit_offset(self, payload):
        limit = int(payload.get("limit") or 50)
        offset = int(payload.get("offset") or 0)
        if limit < 1:
            limit = 50
        if limit > 200:
            limit = 200
        if offset < 0:
            offset = 0
        return limit, offset

    def _get_sale_order_type_items(self):
        field = request.env["sale.order"]._fields.get("sale_order_type")
        selection = field.selection if field else []
        return [{"value": value, "label": label} for value, label in selection]

    def _get_product_price(self, order, product, qty):
        pricelist = order.pricelist_id
        if pricelist:
            try:
                return pricelist.with_context(uom=product.uom_id.id).get_product_price(product, qty, order.partner_id)
            except Exception:
                _logger.debug("Fallback to list_price for product %s", product.id)
        return product.lst_price

    def _prepare_order_line_command(self, order, line_payload):
        product_id = int(line_payload.get("product_id") or 0)
        qty = float(line_payload.get("product_uom_qty") or 0.0)
        if not product_id:
            raise ValueError("Each order line must include product_id")
        if qty <= 0:
            raise ValueError("Each order line must include product_uom_qty greater than 0")

        product = request.env["product.product"].browse(product_id).exists()
        if not product or not product.sale_ok:
            raise ValueError(_("Product %s is not available for sale.") % product_id)

        price_unit = line_payload.get("price_unit")
        if price_unit is None:
            price_unit = self._get_product_price(order, product, qty)
        else:
            price_unit = float(price_unit)

        taxes = product.taxes_id.filtered(lambda tax: not tax.company_id or tax.company_id == order.company_id)
        description = line_payload.get("name") or product.get_product_multiline_description_sale() or product.display_name

        return (
            0,
            0,
            {
                "product_id": product.id,
                "name": description,
                "product_uom_qty": qty,
                "product_uom": product.uom_id.id,
                "price_unit": price_unit,
                "tax_id": [(6, 0, taxes.ids)],
            },
        )

    def _build_aging_buckets(self, lines, today):
        buckets = {
            "current": 0.0,
            "1_30": 0.0,
            "31_60": 0.0,
            "61_90": 0.0,
            "over_90": 0.0,
        }
        for line in lines:
            residual = abs(line.amount_residual)
            if not residual:
                continue
            due_date = line.date_maturity or line.date or today
            overdue_days = (today - due_date).days
            if overdue_days <= 0:
                buckets["current"] += residual
            elif overdue_days <= 30:
                buckets["1_30"] += residual
            elif overdue_days <= 60:
                buckets["31_60"] += residual
            elif overdue_days <= 90:
                buckets["61_90"] += residual
            else:
                buckets["over_90"] += residual
        return buckets

    @http.route("/api/sales/authenticate", type="json", auth="public", methods=["POST"], csrf=False)
    def authenticate(self, **kwargs):
        try:
            data = self._get_json_payload()
            login = (data.get("login") or "").strip()
            password = data.get("password")
            dbname = (data.get("db") or "").strip() or None

            if not login or not password:
                return self._error("login and password are required")

            return self._authenticate_session(login, password, dbname)
        except Exception as exc:
            _logger.exception("Sales JSON-RPC authentication failed")
            return self._error(str(exc))

    @http.route("/api/sales/products", type="json", auth="user", methods=["POST"], csrf=False)
    def get_products(self, **kwargs):
        try:
            payload = self._get_json_payload()
            limit, offset = self._get_limit_offset(payload)
            search = (payload.get("search") or "").strip()

            domain = [("sale_ok", "=", True), ("active", "=", True)]
            if search:
                domain = ["|", ("name", "ilike", search), ("default_code", "ilike", search)] + domain

            products = request.env["product.product"].search(domain, limit=limit, offset=offset, order="default_code, name")
            total = request.env["product.product"].search_count(domain)
            currency = request.env.company.currency_id
            items = [
                {
                    "product_id": product.id,
                    "default_code": product.default_code,
                    "name": product.display_name,
                    "list_price": product.lst_price,
                    "uom_id": product.uom_id.id,
                    "uom_name": product.uom_id.name,
                    "currency_id": currency.id,
                    "currency_name": currency.name,
                }
                for product in products
            ]
            return self._success({"items": items, "count": total})
        except Exception as exc:
            _logger.exception("Failed to fetch products")
            return self._error(str(exc))

    @http.route("/api/sales/payment-terms", type="json", auth="user", methods=["POST"], csrf=False)
    def get_payment_terms(self, **kwargs):
        try:
            payment_terms = request.env["account.payment.term"].search([], order="name")
            items = [
                {"payment_term_id": payment_term.id, "name": payment_term.name}
                for payment_term in payment_terms
            ]
            return self._success({"items": items})
        except Exception as exc:
            _logger.exception("Failed to fetch payment terms")
            return self._error(str(exc))

    @http.route("/api/sales/order-types", type="json", auth="user", methods=["GET"], csrf=False)
    def get_order_types(self, **kwargs):
        try:
            return self._success({"items": self._get_sale_order_type_items()})
        except Exception as exc:
            _logger.exception("Failed to fetch sale order types")
            return self._error(str(exc))

    @http.route("/api/sales/customer-qr-by-id", type="json", auth="user", methods=["POST"], csrf=False)
    def get_customer_qr_by_id(self, **kwargs):
        try:
            payload = self._get_json_payload()
            partner = self._get_partner_by_id(payload.get("customer_id"))
            return self._success(
                {
                    "partner_id": partner.id,
                    "customer_id": partner.id,
                    "name": partner.name,
                    "customer_qr_ref": partner.customer_qr_ref,
                }
            )
        except Exception as exc:
            _logger.exception("Failed to fetch customer QR by id")
            return self._error(str(exc))

    @http.route("/api/sales/customer-qr-payload-by-id", type="json", auth="user", methods=["POST"], csrf=False)
    def get_customer_qr_payload_by_id(self, **kwargs):
        try:
            payload = self._get_json_payload()
            partner = self._get_partner_by_id(payload.get("customer_id"))
            qr_payload = self._build_customer_qr_payload(partner)
            qr_content, qr_format = self._build_qr_content(qr_payload, payload.get("format"))
            return self._success(
                {
                    "partner_id": partner.id,
                    "customer_id": partner.id,
                    "name": partner.name,
                    "customer_qr_ref": partner.customer_qr_ref,
                    "format": qr_format,
                    "qr_content": qr_content,
                    "qr_payload": qr_payload,
                }
            )
        except Exception as exc:
            _logger.exception("Failed to fetch customer QR payload by id")
            return self._error(str(exc))

    @http.route("/api/sales/customer-qr-payload-by-ref", type="json", auth="user", methods=["POST"], csrf=False)
    def get_customer_qr_payload_by_ref(self, **kwargs):
        try:
            payload = self._get_json_payload()
            partner = self._get_partner_by_qr_ref(payload.get("customer_qr_ref"))
            qr_payload = self._build_customer_qr_payload(partner)
            qr_content, qr_format = self._build_qr_content(qr_payload, payload.get("format"))
            return self._success(
                {
                    "partner_id": partner.id,
                    "customer_id": partner.id,
                    "name": partner.name,
                    "customer_qr_ref": partner.customer_qr_ref,
                    "format": qr_format,
                    "qr_content": qr_content,
                    "qr_payload": qr_payload,
                }
            )
        except Exception as exc:
            _logger.exception("Failed to fetch customer QR payload by ref")
            return self._error(str(exc))

    @http.route("/api/sales/customer-detail-by-qr", type="json", auth="user", methods=["POST"], csrf=False)
    def get_customer_detail_by_qr(self, **kwargs):
        try:
            payload = self._get_json_payload()
            partner = self._get_partner_by_qr_ref(payload.get("customer_qr_ref"))
            return self._success(
                {
                    "partner_id": partner.id,
                    "name": partner.name,
                    "customer_qr_ref": partner.customer_qr_ref,
                    "street": partner.street,
                    "street2": partner.street2,
                    "city": partner.city,
                    "phone": partner.phone,
                    "mobile": partner.mobile,
                    "email": partner.email,
                    "payment_term_id": partner.property_payment_term_id.id,
                    "payment_term_name": partner.property_payment_term_id.name,
                }
            )
        except Exception as exc:
            _logger.exception("Failed to fetch customer detail by QR")
            return self._error(str(exc))

    @http.route("/api/sales/customer-accounting-summary-by-qr", type="json", auth="user", methods=["POST"], csrf=False)
    def get_customer_accounting_summary_by_qr(self, **kwargs):
        try:
            payload = self._get_json_payload()
            partner = self._get_partner_by_qr_ref(payload.get("customer_qr_ref"))
            today = fields.Date.today()
            domain_base = [
                ("partner_id", "child_of", partner.id),
                ("move_id.state", "=", "posted"),
                ("reconciled", "=", False),
                ("amount_residual", "!=", 0),
            ]
            receivable_lines = request.env["account.move.line"].search(domain_base + [("account_id.internal_type", "=", "receivable")])
            payable_lines = request.env["account.move.line"].search(domain_base + [("account_id.internal_type", "=", "payable")])

            receivable_total = sum(abs(line.amount_residual) for line in receivable_lines)
            payable_total = sum(abs(line.amount_residual) for line in payable_lines)
            currency = request.env.company.currency_id

            return self._success(
                {
                    "partner_id": partner.id,
                    "customer_qr_ref": partner.customer_qr_ref,
                    "receivable_total": receivable_total,
                    "payable_total": payable_total,
                    "currency": currency.name,
                    "aging_receivable": self._build_aging_buckets(receivable_lines, today),
                    "aging_payable": self._build_aging_buckets(payable_lines, today),
                }
            )
        except Exception as exc:
            _logger.exception("Failed to fetch customer accounting summary by QR")
            return self._error(str(exc))

    @http.route("/api/sales/orders-by-qr", type="json", auth="user", methods=["POST"], csrf=False)
    def get_orders_by_qr(self, **kwargs):
        try:
            payload = self._get_json_payload()
            partner = self._get_partner_by_qr_ref(payload.get("customer_qr_ref"))
            limit, offset = self._get_limit_offset(payload)
            domain = [("partner_id", "child_of", partner.id)]
            orders = request.env["sale.order"].search(domain, limit=limit, offset=offset, order="date_order desc, id desc")
            total = request.env["sale.order"].search_count(domain)
            items = [
                {
                    "sale_order_id": order.id,
                    "name": order.name,
                    "date_order": fields.Datetime.to_string(order.date_order) if order.date_order else False,
                    "commitment_date": fields.Datetime.to_string(order.commitment_date) if order.commitment_date else False,
                    "amount_total": order.amount_total,
                    "state": order.state,
                    "approval_state": order.approval_state,
                    "sale_order_type": order.sale_order_type,
                }
                for order in orders
            ]
            return self._success({"items": items, "count": total})
        except Exception as exc:
            _logger.exception("Failed to fetch orders by QR")
            return self._error(str(exc))

    @http.route("/api/sales/draft-order", type="json", auth="user", methods=["POST"], csrf=False)
    def create_draft_order(self, **kwargs):
        try:
            payload = self._get_json_payload()
            customer_qr_ref = payload.get("customer_qr_ref")
            partner_id = int(payload.get("partner_id") or 0)

            qr_partner = self._get_partner_by_qr_ref(customer_qr_ref) if customer_qr_ref else None
            partner = request.env["res.partner"].browse(partner_id).commercial_partner_id if partner_id else qr_partner
            partner = partner.exists() if partner else partner
            if not partner:
                raise ValueError("partner_id or customer_qr_ref is required")
            if qr_partner and partner != qr_partner:
                raise ValueError("customer_qr_ref does not match partner_id")

            sale_order_type = payload.get("sale_order_type")
            allowed_types = {item["value"] for item in self._get_sale_order_type_items()}
            if sale_order_type not in allowed_types:
                raise ValueError("sale_order_type must be one of: %s" % ", ".join(sorted(allowed_types)))

            commitment_date = payload.get("commitment_date")
            payment_term_id = int(payload.get("payment_term_id") or 0)
            if not commitment_date:
                raise ValueError("commitment_date is required")
            if not payment_term_id:
                raise ValueError("payment_term_id is required")

            payment_term = request.env["account.payment.term"].browse(payment_term_id).exists()
            if not payment_term:
                raise ValueError(_("Payment term %s was not found.") % payment_term_id)

            order_line_payloads = payload.get("order_line") or []
            if not order_line_payloads:
                raise ValueError("order_line must contain at least one item")

            order_vals = {
                "partner_id": partner.id,
                "partner_invoice_id": partner.address_get(["invoice"]).get("invoice") or partner.id,
                "partner_shipping_id": partner.address_get(["delivery"]).get("delivery") or partner.id,
                "pricelist_id": partner.property_product_pricelist.id,
                "payment_term_id": payment_term.id,
                "commitment_date": commitment_date,
                "sale_order_type": sale_order_type,
                "note": payload.get("note") or False,
            }

            optional_int_fields = ["team_id", "business_category_id"]
            for field_name in optional_int_fields:
                if payload.get(field_name):
                    order_vals[field_name] = int(payload[field_name])

            order = request.env["sale.order"].create(order_vals)
            line_commands = [self._prepare_order_line_command(order, line) for line in order_line_payloads]
            order.write({"order_line": line_commands})
            order._amount_all()

            return self._success(
                {
                    "sale_order_id": order.id,
                    "name": order.name,
                    "state": order.state,
                    "amount_total": order.amount_total,
                    "line_count": len(order.order_line),
                },
                "Draft sales order created",
            )
        except Exception as exc:
            _logger.exception("Failed to create draft sales order")
            return self._error(str(exc))
