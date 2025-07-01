odoo.define('sm_insurance.ASDashboardLoad', function (require) {
    'use strict';
    
    var DashBoardData = require('sm_insurance_integration.SMDashboard');

    DashBoardData.include({

        startAutoUpdateDashboard: function() {
            this.$('.btn-success').trigger('click');
        },
        start: function() {
            var def = this._super.apply(this, arguments);
            self._interval = window.setInterval(this.startAutoUpdateDashboard.bind(this), (10000));
            return def;
        },

    });
});
