odoo.define('smartmind_dashboard.OeHealthDashboard', function (require) {
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
    function formatDate(date) {
        var d = new Date(date),
            month = '' + (d.getMonth() + 1),
            day = '' + d.getDate(),
            year = d.getFullYear();

        if (month.length < 2)
            month = '0' + month;
        if (day.length < 2)
            day = '0' + day;

        return [year, month, day].join('-');
    }
    var OehDashBoard = AbstractAction.extend({
        contentTemplate: 'oeHealthdashboard',
        events: {
            'click .load_lab_test': 'load_lab_test',
            'click .load_hvd_appointment': 'load_hvd_appointment',
            'click .load_hvd_appointment_co': 'load_hvd_appointment_co',
            'click .load_physiotherapy_appointment': 'load_physiotherapy_appointment',
            'click .load_physiotherapy_appointment_hp': 'load_physiotherapy_appointment_hp',
            'click .load_physiotherapy_appointment_om': 'load_physiotherapy_appointment_om',
            'click .load_physiotherapy_appointment_te': 'load_physiotherapy_appointment_te',
            'click .load_hhc_appointment': 'load_hhc_appointment',
            'click .load_hhc_appointment_hd': 'load_hhc_appointment_hd',
            'click .load_hhc_appointment_om': 'load_hhc_appointment_om',
            'click .load_hhc_appointment_te': 'load_hhc_appointment_te',
            'click .load_hhc_appointment_hn': 'load_hhc_appointment_hn',
            'click .load_my_hhc_appointment': 'load_my_hhc_appointment',
            'click .load_telemedicine_appointment': 'load_telemedicine_appointment',
            'click .load_telemedicine_appointment_con': 'load_telemedicine_appointment_con',
            'click .load_referral': 'load_referral',
            'click .load_patient': 'load_patient',
            'click .load_my_patient': 'load_my_patient',
            'click .load_physician': 'load_physician',
            'click .load_appointment': 'load_appointment',
            'click .load_my_appointment': 'load_my_appointment',
            'click .load_scheduled_apt': 'load_scheduled_apt',
            'click .load_invoice': 'load_invoice',
            'click .load_treatment': 'load_treatment',
            'click .load_my_treatment': 'load_my_treatment',
            'click .load_lab_request': 'load_lab_request',
            'click .load_image_request': 'load_image_request',
            'click .load_pcr_app': 'load_pcr_app',
            'click .load_pcr_app_c': 'load_pcr_app_c',
            'click .load_pcr_app_t': 'load_pcr_app_t',
            'click .load_investigation_c': 'load_investigation_c',
             'click .load_payment': 'load_payment',
            'click .load_cancellation_refund': 'load_cancellation_refund',
            'click .load_notification': 'load_notification',

            'click #oeh_filter_btn_today': 'oeh_filter_today',
            'click #oeh_filter_btn_week': 'oeh_filter_week',
            'click #oeh_filter_btn_month': 'oeh_filter_month',
            'click #oeh_filter_btn_now': 'oeh_filter_now',
        },

        init: function(parent, context) {
            this._super(parent, context);
            // this.upcoming_events = [];
            this.dashboards_templates = ['OehDashboardFilter','HealthCenterUser','HealthCenterAdmin'];
            this.login_employee = [];
        },

        willStart: function(){
            var self = this;
            this.login_employee = {};
            $('#oeh_curr_day_patient').addClass('d-none');
            $('#oeh_curr_week_patient').addClass('d-none');
            $('#oeh_curr_month_patient').addClass('d-none');
            $('#oeh_total_patient').addClass('d-none');
            return this._super().then(function() {

                var def0 =  self._rpc({
                    model: 'oeh.dashboard',
                    method: 'login_user_group'
                }).then(function(result) {
                 self.group_no = result;
                    /*if (result == 1){
                        self.is_manager = true;
                    }
                    else{
                        self.is_manager = false;
                    }*/
                });
                return $.when(def0);
                // return $.when(def0, def1, def2, def3, def4, def5, def6, def7, def8, def9, def10, def11, def12, def13);
            });
        },

        oeh_filter_today: function (ev) {
            var self = this;

            /* Filter */
            $('.oeh_dashboard_filter_btn .btn').each(function(e){
                this.classList.remove('btn-success')
            })
            ev.currentTarget.classList.add('btn-success')

            /* Dashboard Data */
            rpc.query({
                model: 'oeh.dashboard',
                method: 'oeh_dashboard_today',
                args: [],
            })
            .then(function (result) {
                 /*Cancellation Refund*/
                $('.sm_total_cancellation_refund').empty();
                $('.sm_total_cancellation_refund').append('<h1><b>' + result.cancellation_refund + '</b></h1>');
                /*payment count*/
                $('.sm_total_payment').empty();
                $('.sm_total_payment').append('<h1><b>' + result.payment_count + '</b></h1>');
                /*Investigation*/
                $('.sm_total_investigation').empty();
                $('.sm_total_investigation').append('<h1><b>' + result.investigation_count + '</b></h1>');
                 /*PCR appointment*/
                $('.sm_total_pcr_app').empty();
                $('.sm_total_pcr_app').append('<h1><b>' + result.pcr_app_count + '</b></h1>');
                /*PCR appointment confirmed*/
                $('.sm_total_pcr_app_confirmed').empty();
                $('.sm_total_pcr_app_confirmed').append('<h1><b>' + result.pcr_app_confirmed_count + '</b></h1>');
                 /*PCR appointment team*/
                $('.sm_total_pcr_app_team').empty();
                $('.sm_total_pcr_app_team').append('<h1><b>' + result.pcr_app_team_count + '</b></h1>');
                 /*Image Request*/
                $('.sm_total_image_request').empty();
                $('.sm_total_image_request').append('<h1><b>' + result.image_request_count + '</b></h1>');
                /*Lab Request*/
                $('.sm_total_lab_request').empty();
                $('.sm_total_lab_request').append('<h1><b>' + result.lab_request_count + '</b></h1>');

                /*Image Test*/
                $('.sm_total_image_test').empty();
                $('.sm_total_image_test').append('<h1><b>' + result.image_test_count + '</b></h1>');
                /*Lab Test*/
                $('.sm_total_lab_test').empty();
                $('.sm_total_lab_test').append('<h1><b>' + result.lab_test_count + '</b></h1>');
                /*HVD Appointment*/
                $('.sm_total_hvd').empty();
                $('.sm_total_hvd').append('<h1><b>' + result.hvd_app_count + '</b></h1>');
                $('.sm_total_hvd_c').empty();
                $('.sm_total_hvd_c').append('<h1><b>' + result.hvd_app_confirmed_count + '</b></h1>');
                /*Physiotherapy Appointment*/
                $('.sm_total_phys').empty();
                $('.sm_total_phys').append('<h1><b>' + result.physiotherapy_app_count + '</b></h1>');
                $('.sm_total_phys_hp').empty();
                $('.sm_total_phys_hp').append('<h1><b>' + result.physiotherapy_hp_app_count + '</b></h1>');
                $('.sm_total_phys_om').empty();
                $('.sm_total_phys_om').append('<h1><b>' + result.physiotherapy_om_app_count + '</b></h1>');
                $('.sm_total_phys_t').empty();
                $('.sm_total_phys_t').append('<h1><b>' + result.physiotherapy_t_app_count + '</b></h1>');
                /*HHC Appointment*/
                $('.sm_total_hhc').empty();
                $('.sm_total_hhc').append('<h1><b>' + result.hhc_app_count + '</b></h1>');
                $('.sm_total_hhc_c').empty();
                $('.sm_total_hhc_c').append('<h1><b>' + result.hhc_app_confirmed_count + '</b></h1>');
                $('.sm_total_hhc_hd').empty();
                $('.sm_total_hhc_hd').append('<h1><b>' + result.hhc_app_hd_count + '</b></h1>');
                $('.sm_total_hhc_hn').empty();
                $('.sm_total_hhc_hn').append('<h1><b>' + result.hhc_app_hn_count + '</b></h1>');
                $('.sm_total_hhc_om').empty();
                $('.sm_total_hhc_om').append('<h1><b>' + result.hhc_app_om_count + '</b></h1>');
                $('.sm_total_hhc_t').empty();
                $('.sm_total_hhc_t').append('<h1><b>' + result.hhc_app_t_count + '</b></h1>');
                /*Telemedicine Appointment*/
                $('.sm_total_ta').empty();
                $('.sm_total_ta').append('<h1><b>' + result.scheduled_tele_app_count + '</b></h1>');
                $('.sm_total_tac').empty();
                $('.sm_total_tac').append('<h1><b>' + result.confirmed_tele_app_count + '</b></h1>');

                $('.oeh_total_referral').empty();
                $('.oeh_total_referral').append('<h1><b>' + result.referral_count + '</b></h1>');
                $('.oeh_total_notification').empty();
                $('.oeh_total_notification').append('<h1><b>' + result.notification_count + '</b></h1>');
                /* Patient */
                $('.oeh_total_patient').empty();
                $('.oeh_total_patient').append('<h1><b>' + result.patient_count + '</b></h1>');

                /* MY Patient */
                $('.oeh_total_my_patient').empty();
                $('.oeh_total_my_patient').append('<h1><b>' + result.my_patient_count + '</b></h1>');

                /* Physician */
                $('.oeh_total_physicians').empty();
                $('.oeh_total_physicians').append('<h1><b>' + result.physician_count + '</b></h1>');

                /* Appointment */
                $('.oeh_total_appointment').empty();
                $('.oeh_total_appointment').append('<h1><b>' + result.appointment_count + '</b></h1>');
                /* My HHC Appointment */
                $('.oeh_total_my_hhc_appointment').empty();
                $('.oeh_total_my_hhc_appointment').append('<h1><b>' + result.my_hhc_appointment_count + '</b></h1>');

                /* My Appointment */
                $('.oeh_total_my_appointment').empty();
                $('.oeh_total_my_appointment').append('<h1><b>' + result.my_appointment_count + '</b></h1>');

                /* Scheduled Appointment */
                $('.oeh_total_scheduled_apt').empty();
                $('.oeh_total_scheduled_apt').append('<h1><b>' + result.scheduled_appointment_count + '</b></h1>');

                /* Invoice */
                $('.oeh_total_invoices').empty();
                $('.oeh_total_invoices').append('<h1><b>' + result.invoice_count + '</b></h1>');

                /* Treatment */
                $('.oeh_total_treatments').empty();
                $('.oeh_total_treatments').append('<h1><b>' + result.treatment_count + '</b></h1>');

                /* My Treatment */
                $('.oeh_total_my_treatments').empty();
                $('.oeh_total_my_treatments').append('<h1><b>' + result.my_treatment_count + '</b></h1>');
            })
        },

        oeh_filter_week: function (ev) {
            var self = this;
            
            /* Filter */
            $('.oeh_dashboard_filter_btn .btn').each(function(e){
                this.classList.remove('btn-success')
            })
            ev.currentTarget.classList.add('btn-success')
            
            /* Dashboard Data */
            rpc.query({
                model: 'oeh.dashboard',
                method: 'oeh_filter_week',
                args: [],
            })
            .then(function (result) {
                /*Cancellation Refund*/
                $('.sm_total_cancellation_refund').empty();
                $('.sm_total_cancellation_refund').append('<h1><b>' + result.cancellation_refund + '</b></h1>');
                /*payment count*/
                $('.sm_total_payment').empty();
                $('.sm_total_payment').append('<h1><b>' + result.payment_count + '</b></h1>');
                /*Investigation*/
                $('.sm_total_investigation').empty();
                $('.sm_total_investigation').append('<h1><b>' + result.investigation_count + '</b></h1>');

                /*PCR appointment*/
                $('.sm_total_pcr_app').empty();
                $('.sm_total_pcr_app').append('<h1><b>' + result.pcr_app_count + '</b></h1>');
                /*PCR appointment confirmed*/
                $('.sm_total_pcr_app_confirmed').empty();
                $('.sm_total_pcr_app_confirmed').append('<h1><b>' + result.pcr_app_confirmed_count + '</b></h1>');
                  /*PCR appointment team*/
                $('.sm_total_pcr_app_team').empty();
                $('.sm_total_pcr_app_team').append('<h1><b>' + result.pcr_app_team_count + '</b></h1>');

                 /*Image Request*/
                $('.sm_total_image_request').empty();
                $('.sm_total_image_request').append('<h1><b>' + result.image_request_count + '</b></h1>');
                /*Lab Request*/
                $('.sm_total_lab_request').empty();
                $('.sm_total_lab_request').append('<h1><b>' + result.lab_request_count + '</b></h1>');

                /*Image Test*/
                $('.sm_total_image_test').empty();
                $('.sm_total_image_test').append('<h1><b>' + result.image_test_count + '</b></h1>');
                /*Lab Test*/
                $('.sm_total_lab_test').empty();
                $('.sm_total_lab_test').append('<h1><b>' + result.lab_test_count + '</b></h1>');
                /*HVD Appointment*/
                $('.sm_total_hvd').empty();
                $('.sm_total_hvd').append('<h1><b>' + result.hvd_app_count + '</b></h1>');
                $('.sm_total_hvd_c').empty();
                $('.sm_total_hvd_c').append('<h1><b>' + result.hvd_app_confirmed_count + '</b></h1>');
                /*Physiotherapy Appointment*/
                $('.sm_total_phys').empty();
                $('.sm_total_phys').append('<h1><b>' + result.physiotherapy_app_count + '</b></h1>');
                $('.sm_total_phys_hp').empty();
                $('.sm_total_phys_hp').append('<h1><b>' + result.physiotherapy_hp_app_count + '</b></h1>');
                $('.sm_total_phys_om').empty();
                $('.sm_total_phys_om').append('<h1><b>' + result.physiotherapy_om_app_count + '</b></h1>');
                $('.sm_total_phys_t').empty();
                $('.sm_total_phys_t').append('<h1><b>' + result.physiotherapy_t_app_count + '</b></h1>');
                /*HHC Appointment*/
                $('.sm_total_hhc').empty();
                $('.sm_total_hhc').append('<h1><b>' + result.hhc_app_count + '</b></h1>');
                $('.sm_total_hhc_c').empty();
                $('.sm_total_hhc_c').append('<h1><b>' + result.hhc_app_confirmed_count + '</b></h1>');
                $('.sm_total_hhc_hd').empty();
                $('.sm_total_hhc_hd').append('<h1><b>' + result.hhc_app_hd_count + '</b></h1>');
                $('.sm_total_hhc_hn').empty();
                $('.sm_total_hhc_hn').append('<h1><b>' + result.hhc_app_hn_count + '</b></h1>');
                $('.sm_total_hhc_om').empty();
                $('.sm_total_hhc_om').append('<h1><b>' + result.hhc_app_om_count + '</b></h1>');
                $('.sm_total_hhc_t').empty();
                $('.sm_total_hhc_t').append('<h1><b>' + result.hhc_app_t_count + '</b></h1>');
                /*Telemedicine Appointment*/
                $('.sm_total_ta').empty();
                $('.sm_total_ta').append('<h1><b>' + result.scheduled_tele_app_count + '</b></h1>');
                $('.sm_total_tac').empty();
                $('.sm_total_tac').append('<h1><b>' + result.confirmed_tele_app_count + '</b></h1>');

                $('.oeh_total_referral').empty();
                $('.oeh_total_referral').append('<h1><b>' + result.referral_count + '</b></h1>');
                /* Patient */
                $('.oeh_total_patient').empty();
                $('.oeh_total_patient').append('<h1><b>' + result.patient_count + '</b></h1>');

                /* MY Patient */
                $('.oeh_total_my_patient').empty();
                $('.oeh_total_my_patient').append('<h1><b>' + result.my_patient_count + '</b></h1>');

                /* Physician */
                $('.oeh_total_physicians').empty();
                $('.oeh_total_physicians').append('<h1><b>' + result.physician_count + '</b></h1>');

                /* Appointment */
                $('.oeh_total_appointment').empty();
                $('.oeh_total_appointment').append('<h1><b>' + result.appointment_count + '</b></h1>');

                /* My Appointment */
                $('.oeh_total_my_appointment').empty();
                $('.oeh_total_my_appointment').append('<h1><b>' + result.my_appointment_count + '</b></h1>');

                /* Scheduled Appointment */
                $('.oeh_total_scheduled_apt').empty();
                $('.oeh_total_scheduled_apt').append('<h1><b>' + result.scheduled_appointment_count + '</b></h1>');

                /* Invoice */
                $('.oeh_total_invoices').empty();
                $('.oeh_total_invoices').append('<h1><b>' + result.invoice_count + '</b></h1>');

                /* Treatment */
                $('.oeh_total_treatments').empty();
                $('.oeh_total_treatments').append('<h1><b>' + result.treatment_count + '</b></h1>');

                /* My Treatment */
                $('.oeh_total_my_treatments').empty();
                $('.oeh_total_my_treatments').append('<h1><b>' + result.my_treatment_count + '</b></h1>');
            })
        },

        oeh_filter_month: function (ev) {
            var self = this;

            /* Filter */
            $('.oeh_dashboard_filter_btn .btn').each(function(e){
                this.classList.remove('btn-success')
            })
            ev.currentTarget.classList.add('btn-success')

            /* Dashboard Data */
            rpc.query({
                model: 'oeh.dashboard',
                method: 'oeh_filter_month',
                args: [],
            })
            .then(function (result) {
                console.log(result)
                /*Cancellation Refund*/
                $('.sm_total_cancellation_refund').empty();
                $('.sm_total_cancellation_refund').append('<h1><b>' + result.cancellation_refund + '</b></h1>');
                /*payment count*/
                $('.sm_total_payment').empty();
                $('.sm_total_payment').append('<h1><b>' + result.payment_count + '</b></h1>');
                /*Investigation*/
                $('.sm_total_investigation').empty();
                $('.sm_total_investigation').append('<h1><b>' + result.investigation_count + '</b></h1>');

                 /*PCR appointment*/
                $('.sm_total_pcr_app').empty();
                $('.sm_total_pcr_app').append('<h1><b>' + result.pcr_app_count + '</b></h1>');
                /*PCR appointment confirmed*/
                $('.sm_total_pcr_app_confirmed').empty();
                $('.sm_total_pcr_app_confirmed').append('<h1><b>' + result.pcr_app_confirmed_count + '</b></h1>');
                  /*PCR appointment team*/
                $('.sm_total_pcr_app_team').empty();
                $('.sm_total_pcr_app_team').append('<h1><b>' + result.pcr_app_team_count + '</b></h1>');

                 /*Image Request*/
                $('.sm_total_image_request').empty();
                $('.sm_total_image_request').append('<h1><b>' + result.image_request_count + '</b></h1>');
                /*Lab Request*/
                $('.sm_total_lab_request').empty();
                $('.sm_total_lab_request').append('<h1><b>' + result.lab_request_count + '</b></h1>');

                /*Image Test*/
                $('.sm_total_image_test').empty();
                $('.sm_total_image_test').append('<h1><b>' + result.image_test_count + '</b></h1>');
                /*Lab Test*/
                $('.sm_total_lab_test').empty();
                $('.sm_total_lab_test').append('<h1><b>' + result.lab_test_count + '</b></h1>');
                /*HVD Appointment*/
                $('.sm_total_hvd').empty();
                $('.sm_total_hvd').append('<h1><b>' + result.hvd_app_count + '</b></h1>');
                $('.sm_total_hvd_c').empty();
                $('.sm_total_hvd_c').append('<h1><b>' + result.hvd_app_confirmed_count + '</b></h1>');
                /*Physiotherapy Appointment*/
                $('.sm_total_phys').empty();
                $('.sm_total_phys').append('<h1><b>' + result.physiotherapy_app_count + '</b></h1>');
                $('.sm_total_phys_hp').empty();
                $('.sm_total_phys_hp').append('<h1><b>' + result.physiotherapy_hp_app_count + '</b></h1>');
                $('.sm_total_phys_om').empty();
                $('.sm_total_phys_om').append('<h1><b>' + result.physiotherapy_om_app_count + '</b></h1>');
                $('.sm_total_phys_t').empty();
                $('.sm_total_phys_t').append('<h1><b>' + result.physiotherapy_t_app_count + '</b></h1>');
                /*HHC Appointment*/
                $('.sm_total_hhc').empty();
                $('.sm_total_hhc').append('<h1><b>' + result.hhc_app_count + '</b></h1>');
                $('.sm_total_hhc_c').empty();
                $('.sm_total_hhc_c').append('<h1><b>' + result.hhc_app_confirmed_count + '</b></h1>');
                $('.sm_total_hhc_hd').empty();
                $('.sm_total_hhc_hd').append('<h1><b>' + result.hhc_app_hd_count + '</b></h1>');
                $('.sm_total_hhc_hn').empty();
                $('.sm_total_hhc_hn').append('<h1><b>' + result.hhc_app_hn_count + '</b></h1>');
                $('.sm_total_hhc_om').empty();
                $('.sm_total_hhc_om').append('<h1><b>' + result.hhc_app_om_count + '</b></h1>');
                $('.sm_total_hhc_t').empty();
                $('.sm_total_hhc_t').append('<h1><b>' + result.hhc_app_t_count + '</b></h1>');
                /*Telemedicine Appointment*/
                $('.sm_total_ta').empty();
                $('.sm_total_ta').append('<h1><b>' + result.scheduled_tele_app_count + '</b></h1>');
                $('.sm_total_tac').empty();
                $('.sm_total_tac').append('<h1><b>' + result.confirmed_tele_app_count + '</b></h1>');

                $('.oeh_total_referral').empty();
                $('.oeh_total_referral').append('<h1><b>' + result.referral_count + '</b></h1>');
                /* Patient */
                $('.oeh_total_patient').empty();
                $('.oeh_total_patient').append('<h1><b>' + result.patient_count + '</b></h1>');

                /* MY Patient */
                $('.oeh_total_my_patient').empty();
                $('.oeh_total_my_patient').append('<h1><b>' + result.my_patient_count + '</b></h1>');

                /* Physician */
                $('.oeh_total_physicians').empty();
                $('.oeh_total_physicians').append('<h1><b>' + result.physician_count + '</b></h1>');

                /* Appointment */
                $('.oeh_total_appointment').empty();
                $('.oeh_total_appointment').append('<h1><b>' + result.appointment_count + '</b></h1>');

                /* My Appointment */
                $('.oeh_total_my_appointment').empty();
                $('.oeh_total_my_appointment').append('<h1><b>' + result.my_appointment_count + '</b></h1>');

                /* Scheduled Appointment */
                $('.oeh_total_scheduled_apt').empty();
                $('.oeh_total_scheduled_apt').append('<h1><b>' + result.scheduled_appointment_count + '</b></h1>');

                /* Invoice */
                $('.oeh_total_invoices').empty();
                $('.oeh_total_invoices').append('<h1><b>' + result.invoice_count + '</b></h1>');

                /* Treatment */
                $('.oeh_total_treatments').empty();
                $('.oeh_total_treatments').append('<h1><b>' + result.treatment_count + '</b></h1>');

                /* My Treatment */
                $('.oeh_total_my_treatments').empty();
                $('.oeh_total_my_treatments').append('<h1><b>' + result.my_treatment_count + '</b></h1>');
            })
        },

        oeh_filter_now: function (ev) {
            var self = this;
            /* Filter */
            $('.oeh_dashboard_filter_btn .btn').each(function(e){
                this.classList.remove('btn-success')
            })
            ev.currentTarget.classList.add('btn-success')

            /* Dashboard Data */
            rpc.query({
                model: 'oeh.dashboard',
                method: 'oeh_filter_now',
                args: [],
            })
            .then(function (result) {
                console.log
                /*Cancellation Refund*/
                $('.sm_total_cancellation_refund').empty();
                $('.sm_total_cancellation_refund').append('<h1><b>' + result.cancellation_refund + '</b></h1>');
                /*payment count*/
                $('.sm_total_payment').empty();
                $('.sm_total_payment').append('<h1><b>' + result.payment_count + '</b></h1>');
                /*Investigation*/
                $('.sm_total_investigation').empty();
                $('.sm_total_investigation').append('<h1><b>' + result.investigation_count + '</b></h1>');

                 /*PCR appointment*/
                $('.sm_total_pcr_app').empty();
                $('.sm_total_pcr_app').append('<h1><b>' + result.pcr_app_count + '</b></h1>');
                /*PCR appointment confirmed*/
                $('.sm_total_pcr_app_confirmed').empty();
                $('.sm_total_pcr_app_confirmed').append('<h1><b>' + result.pcr_app_confirmed_count + '</b></h1>');
                 /*PCR appointment team*/
                $('.sm_total_pcr_app_team').empty();
                $('.sm_total_pcr_app_team').append('<h1><b>' + result.pcr_app_team_count + '</b></h1>');

                /*Image Request*/
                $('.sm_total_image_request').empty();
                $('.sm_total_image_request').append('<h1><b>' + result.image_request_count + '</b></h1>');
                /*Lab Request*/
                $('.sm_total_lab_request').empty();
                $('.sm_total_lab_request').append('<h1><b>' + result.lab_request_count + '</b></h1>');

                /*Image Test*/
                $('.sm_total_image_test').empty();
                $('.sm_total_image_test').append('<h1><b>' + result.image_test_count + '</b></h1>');
                /*Lab Test*/
                $('.sm_total_lab_test').empty();
                $('.sm_total_lab_test').append('<h1><b>' + result.lab_test_count + '</b></h1>');
                /*HVD Appointment*/
                $('.sm_total_hvd').empty();
                $('.sm_total_hvd').append('<h1><b>' + result.hvd_app_count + '</b></h1>');
                $('.sm_total_hvd_c').empty();
                $('.sm_total_hvd_c').append('<h1><b>' + result.hvd_app_confirmed_count + '</b></h1>');
                /*Physiotherapy Appointment*/
                $('.sm_total_phys').empty();
                $('.sm_total_phys').append('<h1><b>' + result.physiotherapy_app_count + '</b></h1>');
                $('.sm_total_phys_hp').empty();
                $('.sm_total_phys_hp').append('<h1><b>' + result.physiotherapy_hp_app_count + '</b></h1>');
                $('.sm_total_phys_om').empty();
                $('.sm_total_phys_om').append('<h1><b>' + result.physiotherapy_om_app_count + '</b></h1>');
                $('.sm_total_phys_t').empty();
                $('.sm_total_phys_t').append('<h1><b>' + result.physiotherapy_t_app_count + '</b></h1>');
                /*HHC Appointment*/
                $('.sm_total_hhc').empty();
                $('.sm_total_hhc').append('<h1><b>' + result.hhc_app_count + '</b></h1>');
                $('.sm_total_hhc_c').empty();
                $('.sm_total_hhc_c').append('<h1><b>' + result.hhc_app_confirmed_count + '</b></h1>');
                $('.sm_total_hhc_hd').empty();
                $('.sm_total_hhc_hd').append('<h1><b>' + result.hhc_app_hd_count + '</b></h1>');
                $('.sm_total_hhc_hn').empty();
                $('.sm_total_hhc_hn').append('<h1><b>' + result.hhc_app_hn_count + '</b></h1>');
                $('.sm_total_hhc_om').empty();
                $('.sm_total_hhc_om').append('<h1><b>' + result.hhc_app_om_count + '</b></h1>');
                $('.sm_total_hhc_t').empty();
                $('.sm_total_hhc_t').append('<h1><b>' + result.hhc_app_t_count + '</b></h1>');
                /*Telemedicine Appointment*/
                $('.sm_total_ta').empty();
                $('.sm_total_ta').append('<h1><b>' + result.scheduled_tele_app_count + '</b></h1>');
                $('.sm_total_tac').empty();
                $('.sm_total_tac').append('<h1><b>' + result.confirmed_tele_app_count + '</b></h1>');

                $('.oeh_total_referral').empty();
                $('.oeh_total_referral').append('<h1><b>' + result.referral_count + '</b></h1>');
                /* Patient */
                $('.oeh_total_patient').empty();
                $('.oeh_total_patient').append('<h1><b>' + result.patient_count + '</b></h1>');

                /* MY Patient */
                $('.oeh_total_my_patient').empty();
                $('.oeh_total_my_patient').append('<h1><b>' + result.my_patient_count + '</b></h1>');

                /* Physician */
                $('.oeh_total_physicians').empty();
                $('.oeh_total_physicians').append('<h1><b>' + result.physician_count + '</b></h1>');

                /* Appointment */
                $('.oeh_total_appointment').empty();
                $('.oeh_total_appointment').append('<h1><b>' + result.appointment_count + '</b></h1>');

                /* My Appointment */
                $('.oeh_total_my_appointment').empty();
                $('.oeh_total_my_appointment').append('<h1><b>' + result.my_appointment_count + '</b></h1>');

                /* Scheduled Appointment */
                $('.oeh_total_scheduled_apt').empty();
                $('.oeh_total_scheduled_apt').append('<h1><b>' + result.scheduled_appointment_count + '</b></h1>');

                /* Invoice */
                $('.oeh_total_invoices').empty();
                $('.oeh_total_invoices').append('<h1><b>' + result.invoice_count + '</b></h1>');

                /* Treatment */
                $('.oeh_total_treatments').empty();
                $('.oeh_total_treatments').append('<h1><b>' + result.treatment_count + '</b></h1>');

                /* My Treatment */
                $('.oeh_total_my_treatments').empty();
                $('.oeh_total_my_treatments').append('<h1><b>' + result.my_treatment_count + '</b></h1>');
            })
        },

        renderElement: function (ev) {
            var self = this;
            $.when(this._super())
            .then(function (ev) {
                $('#oeh_filter_btn_today').click()
            });
        },
        /* Load Lab Test */
        load_lab_test: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HVD Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hvd.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'Confirmed']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load HVD Appointment */
        load_hvd_appointment: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HVD Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hvd.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'Scheduled']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load HVD Appointment CO*/
        load_hvd_appointment_co: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HVD Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hvd.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'Confirmed']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load Physiotherapy Appointment */
        load_physiotherapy_appointment: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Physiotherapy Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.physiotherapy.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'scheduled']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load Physiotherapy Appointment HP */
        load_physiotherapy_appointment_hp: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Physiotherapy Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.physiotherapy.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'confirmed']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load Physiotherapy Appointment OM */
        load_physiotherapy_appointment_om: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Physiotherapy Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.physiotherapy.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'operation_manager']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load Physiotherapy Appointment TE */
        load_physiotherapy_appointment_te: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Physiotherapy Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.physiotherapy.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'team']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load HHC Appointment */
        load_hhc_appointment: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'scheduled']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load HHC Appointment HD*/
        load_hhc_appointment_hd: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'confirmed']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load HHC Appointment OM*/
        load_hhc_appointment_om: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'operation_manager']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load HHC Appointment TE*/
        load_hhc_appointment_te: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'team']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load HHC Appointment HN*/
        load_hhc_appointment_hn: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'start']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load Telemedicine Appointment */
        load_telemedicine_appointment: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Telemedicine Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'Scheduled']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load Telemedicine Appointment Con */
        load_telemedicine_appointment_con: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Telemedicine Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'Confirmed']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load Referral */
        load_referral: function(e) {
        var today = new Date()
        var datenow = formatDate(today)
        console.log(datenow)
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Referral"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.referral',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'call_center']],
//                domain: [('create_date', '=', datenow)],
//                domin: [('create_date', '&gt;=',(context_today()--relativedelta(day=context_today().weekday())).strftime('%Y-%m-%d')),]
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load Patient */
        load_patient: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Patients"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.patient',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                // domain: [['user_id', '=', session.uid]],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load MY Patient */
        load_my_patient: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Patients"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.patient',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                // domain: [['user_id', '=', session.uid]],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load Physician */
        load_physician: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Physician"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.physician',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                // domain: [['user_id', '=', session.uid]],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load Appointment */
        load_appointment: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                // domain: [['user_id', '=', session.uid]],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load MY  Appointment */
        load_my_appointment: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Physician"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
         /* Load MY HHC Appointment */
        load_my_hhc_appointment: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Physician"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                target: 'current',
                domain: [['state', '=', 'team']],
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load Schedule */
        load_scheduled_apt: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Schedule"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load Invoice */
        load_invoice: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Invoice"),
                type: 'ir.actions.act_window',
                res_model: 'account.move',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                // domain: [['user_id', '=', session.uid]],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load Treatments */
        load_treatment: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Treatments"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.treatment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                // domain: [['user_id', '=', session.uid]],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load MY Treatments */
        load_my_treatment: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("MY Treatments"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.treatment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                // domain: [['user_id', '=', session.uid]],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load Lab Request */
        load_lab_request: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Lab Request"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.lab.request',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'Call Center']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load Image Request */
        load_image_request: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Imaging Request"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.imaging.request',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'Call Center']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load PCR appointment */
        load_pcr_app: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("PCR Appointmrnt"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.pcr.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'scheduled']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load Payment */
        load_payment: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Requested Payments"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.requested.payments',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'Send']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load Cancellation Refund */
        load_cancellation_refund: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Cancellation and Refund"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.cancellation.refund',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'Send']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load Notification */
        load_notification: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Notification"),
                type: 'ir.actions.act_window',
                res_model: 'sm.physician.notification',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'Send']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load PCR appointment confirmed */
        load_pcr_app_c: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("PCR Appointmrnt"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.pcr.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'confirmed']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
        /* Load PCR appointment confirmed */
        load_pcr_app_t: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("PCR Appointmrnt"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.pcr.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'team']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },
         /* Load Investigation */
        load_investigation_c: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Investigation"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.investigation',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'],[false, 'form'],[false, 'kanban']],
                domain: [['state', '=', 'Call Center']],
                target: 'current',
            }, {reverse_breadcrumb: this.reverse_breadcrumb})
        },

        start: function() {
            var self = this;
            this.set("title", 'Sehati Dashboard');
            return this._super().then(function() {
                self.update_cp();
                self.render_dashboards();
                console.log(self)
            });
        },

        fetch_data: function() {
            var self = this;

            var def0 =  self._rpc({
                model: 'oeh.dashboard',
                method: 'login_user_group'
            }).then(function(result) {
                self.group_no = result;
                /*if (result == 1){
                    self.is_manager = true;
                }
                else{
                    self.is_manager = false;
                }*/
            });

            return $.when(def0);
        },

        render_dashboards: function() {
            var self = this;
            if (this.login_employee){
                var templates = []
                switch(self.group_no){
                    case 1:
                        templates = ['OehDashboardFilter','HealthCenterAdmin'];
                        break;
                    case 2:
                        templates = ['OehDashboardFilter','HealthCenterAdmin'];
                        break;
                    case 3:
                        templates = ['OehDashboardFilter','HealthCenterAdmin'];
                        break;
                    case 4:
                        templates = ['OehDashboardFilter','HealthHeadDoctor'];
                        break;
                    case 5:
                        templates = ['OehDashboardFilter','HealthHHCDoctor'];
                        break;
                    case 6:
                        templates = ['OehDashboardFilter','HealthTelemedicineDoctor'];
                        break;
                    case 7:
                        templates = ['OehDashboardFilter','HealthHeadNurse'];
                        break;
                    case 8:
                        templates = ['OehDashboardFilter','HealthHeadPhysiotherapist'];
                        break;
                    case 9:
                        templates = ['OehDashboardFilter','HealthHHCNurse'];
                        break;
                    case 10:
                        templates = ['OehDashboardFilter','HealthHHCPhysiotherapist'];
                        break;
                    case 11:
                        templates = ['OehDashboardFilter','HealthOperationsManager'];
                        break;
                    case 12:
                        templates = ['OehDashboardFilter','HealthLabTechnician'];
                        break;
                }

                /*if( self.is_manager == true){
                    templates = ['OehDashboardFilter','HealthCenterAdmin'];
                }
                else{
                    templates = ['OehDashboardFilter','HealthCenterUser'];
                }*/
                _.each(templates, function(template) {
                    self.$('.oeh_main_dashboard').append(QWeb.render(template, {widget: self}));
                });
            }
            else{
                self.$('.oeh_main_dashboard').append(QWeb.render('EmployeeWarning', {widget: self}));
            }
        },

        reverse_breadcrumb: function() {
            var self = this;
            web_client.do_push_state({});
            // this.update_cp();
            this.fetch_data().then(function() {
                self.$('.oeh_main_dashboard').reload();
                self.render_dashboards();
            });
        },

        update_cp: function() {
            var self = this;
        },
    });

    core.action_registry.add('smartmind_dashboard', OehDashBoard);
    return OehDashBoard;
});