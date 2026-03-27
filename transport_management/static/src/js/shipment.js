odoo.define('transport_management.ShipmentDashboard', function (require) {
    'use strict';
    const AbstractAction = require('web.AbstractAction');
    const ajax = require('web.ajax');
    const core = require('web.core');
    const rpc = require('web.rpc');
    const session = require('web.session')
    const web_client = require('web.web_client');
    const _t = core._t;
    const QWeb = core.qweb;

    const ActionMenu = AbstractAction.extend({

        template: 'shipmentDashboard',

        events: {
            'click .shipment-stats': 'view_shipment_stats',
        },
        renderElement: function (ev) {
            const self = this;
            $.when(this._super())
                .then(function (ev) {
                    rpc.query({
                        model: "transport.shipment",
                        method: "get_shipment_stats",
                    }).then(function (result) {
                        $('#ts_all_count').empty().append(result['all']);
                        $('#ts_pack_count').empty().append(result['pack']);
                        $('#ts_ship_count').empty().append(result['ship']);
                        $('#ts_in_transit_count').empty().append(result['transit']);
                        $('#ts_done_count').empty().append(result['done']);
                        $('#ts_cancel_count').empty().append(result['cancel']);
                    });
                });
        },
        view_shipment_stats : function (ev){
            let type = $(ev.currentTarget).data('type');
            if(type === 'all'){
                 this.get_action(ev, []);
            }
            else {
                 this.get_action(ev, [['status', '=', type]]);
            }
        },
        get_action: function (ev, filter){
            ev.preventDefault();
            return this.do_action({
                name: _t("Transport Shipment"),
                type: 'ir.actions.act_window',
                res_model: 'transport.shipment',
                domain: filter,
                views: [[false, 'kanban'],[false, 'tree'],[false, 'form']],
                target: 'current'
            });
        },

        willStart: function () {
            const self = this;
            self.drpdn_show = false;
            return Promise.all([ajax.loadLibs(this), this._super()]);
        },
    });
    core.action_registry.add('shipment_dashboard', ActionMenu);

});
