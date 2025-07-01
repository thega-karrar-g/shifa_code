odoo.define('smartmind_dashboard.DashboardData', function (require) {
    'use strict';

    var AbstractAction = require('web.AbstractAction');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var web_client = require('web.web_client');
    var session = require('web.session');
    var _t = core._t;
    var QWeb = core.qweb;
    var self = this;
    var currency;

    var DashBoardData = require('smartmind_dashboard.DashboardData');
    console.log(DashBoardData);

    DashBoardData.include({
        willStart: function(){
            var self = this;
            this.login_employee = {};
            $('#oeh_curr_day_patient').addClass('d-none');
            $('#oeh_curr_week_patient').addClass('d-none');
            $('#oeh_curr_month_patient').addClass('d-none');
            $('#oeh_total_patient').addClass('d-none');
            this.call('bus_service', 'onNotification', this, this._onLongpollingNotifications);
            return this._super().then(function() {

                var def0 =  self._rpc({
                    model: 'sm.dashboard',
                    method: 'login_user_group'
                }).then(function(result) {
                 self.group_no = result;
                });
                return $.when(def0);
            });
        },

        async _onLongpollingNotifications(notifications) {
            this.$('#oeh_filter_btn_today').trigger('click');
        },

        startAutoUpdateDashboard: function() {
            setInterval(() => {
                this.$('#oeh_filter_btn_today').trigger('click');
            }, 20000);
        },

        start: function() {
            this._super();
            this.startAutoUpdateDashboard();
        },

    });
});
