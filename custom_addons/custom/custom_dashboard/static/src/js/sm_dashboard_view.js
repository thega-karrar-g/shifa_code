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
    var ids_tele_sch, ids_tele_con, ids_tele_sch_con, ids_hvd_sch, ids_hvd_con, ids_hvd_sch_con, ids_physiotherapy_sc,
        ids_physiotherapy_co, ids_physiotherapy_op, ids_physiotherapy_tm, ids_phy_all, ids_hhc_sch, ids_hhc_hd, ids_hhc_hn,
        ids_hhc_om, ids_hhc_tm, ids_hhc_all, ids_tele_today, ids_hvd_today, ids_hhc_today, ids_phy_today, ids_pcr_today,
        ids_pcr_sch, ids_pcr_opm, ids_pcr_tm, ids_pcr_all, ids_ser_req, ids_not, ids_image_req, ids_lab_rec, ids_inve, ids_ref,
        ids_payments, ids_paid_payment, ids_cancellation, ids_hhc_tod_tm_res_the, ids_tele_tod_tm_res_the, ids_hhc_tod_tm_soc_wor, ids_tele_tod_con_soc_wor,
        ids_hhc_tod_tm_hhc_nurse, ids_tele_tod_con_hhc_nurse, ids_pcr_tod_team_hhc_nurse, ids_pcr_tod_team_lab_technician, ids_phy_tod_team_hhc_phy,
        ids_hhc_tod_team_hhc_phy, ids_tele_tod_con_hhc_phy, ids_tele_tod_con_tele_app, ids_hhc_tod_team_hhc_doctor, ids_tele_tod_con_hhc_doctor,
        ids_hvd_tod_con_hhc_doctor, ids_tele_tod_con_head_phy, ids_hhc_tod_tm_head_phy, ids_phy_tod_tm_head_phy, ids_hhc_tod_tm_head_nurse,
        ids_pcr_tod_tm_head_nurse, ids_hvd_tod_con_head_doctor, ids_hhc_tod_tm_head_doctor, ids_call_center, ids_call_center_op, ids_hhc_vd,
        ids_hhc_inp, ids_hhc_ca, ids_web_req, ids_physiotherapy_inp, ids_physiotherapy_vd, ids_physiotherapy_ca, ids_pr_cancellation, ids_op_cancellation, ids_send_payments,
        ids_slep_me_req_unpaid, ids_slep_me_req_paid, ids_slep_me_req_ev, ids_slep_me_req_sch,
        ids_car_cont_unpaid, ids_car_cont_paid, ids_car_cont_ev, ids_car_cont_as_car, ids_car_cont_act, ids_car_cont_rea_req,
        ids_car_cont_hrq, ids_car_cont_trq, ids_car_cont_rew, ids_car_cont_hol,
        ids_hhc_app_cr, ids_phy_app_cr, ids_draft_payment,

        ids_my_hhc_app_tem, ids_my_hhc_app_phys_tem, ids_my_rh_hhc_app_tem, ids_my_rh_tele_con, ids_my_rh_hvd_con,
        ids_my_physiotherapy_app_tem, ids_my_physiotherapy_app_sch, ids_my_physiotherapy_app_hp, ids_my_physiotherapy_app_op, ids_my_h_hhc_app_tem,
        ids_my_tele_con, ids_my_hvd_con, ids_my_hn_tele_con, ids_my_hdphy_tele_con, ids_my_hhcn_tele_con, ids_my_hhcn_pcr_con, ids_my_hhcphy_pcr_con, ids_missed_medicine, ids_cancel_medicine = new Array();
    function setCountValueToXml(className, count) {
        $(className).empty();
        $(className).append('<h1><b>' + count + '</b></h1>');
    }
    var OehDashBoard = AbstractAction.extend({
        contentTemplate: 'smHealthDashboard',

        events: {
            'click .load_telemedicine_appointment': 'load_telemedicine_appointment',
            'click .load_caregive_missed_medicines': 'load_caregive_missed_medicines',
            'click .load_caregiver_canceled_medicines': 'load_caregiver_canceled_medicines',
            'click .create_telemedicine_appointment': 'create_telemedicine_appointment',
            'click .create_hvd_appointment': 'create_hvd_appointment',
            'click .create_pt_appointment': 'create_pt_appointment',
            'click .create_hhc_appointment': 'create_hhc_appointment',
            'click .create_call_center': 'create_call_center',
            'click .load_telemedicine_appointment_con': 'load_telemedicine_appointment_con',
            'click .load_tele_sch_con_appointment': 'load_tele_sch_con_appointment',
            'click .load_hvd_appointment': 'load_hvd_appointment',
            'click .load_hvd_appointment_co': 'load_hvd_appointment_co',
            'click .load_hvd_sch_con_appointment': 'load_hvd_sch_con_appointment',
            'click .load_physiotherapy_appointment': 'load_physiotherapy_appointment',
            'click .load_physiotherapy_appointment_hp': 'load_physiotherapy_appointment_hp',
            'click .load_physiotherapy_appointment_om': 'load_physiotherapy_appointment_om',
            'click .load_physiotherapy_appointment_te': 'load_physiotherapy_appointment_te',
            'click .load_physiotherapy_appointment_inp': 'load_physiotherapy_appointment_inp',
            'click .load_physiotherapy_appointment_vd': 'load_physiotherapy_appointment_vd',
            'click .load_physiotherapy_appointment_ca': 'load_physiotherapy_appointment_ca',
            'click .load_phy_all_appointment': 'load_phy_all_appointment',
            'click .load_hhc_appointment': 'load_hhc_appointment',
            'click .load_hhc_appointment_hd': 'load_hhc_appointment_hd',
            'click .load_hhc_appointment_hn': 'load_hhc_appointment_hn',
            'click .load_hhc_appointment_om': 'load_hhc_appointment_om',
            'click .load_hhc_appointment_te': 'load_hhc_appointment_te',
            'click .load_hhc_all_appointment': 'load_hhc_all_appointment',
            'click .load_tele_appointment_today': 'load_tele_appointment_today',
            'click .load_hvd_appointment_today': 'load_hvd_appointment_today',
            'click .load_hhc_appointment_today': 'load_hhc_appointment_today',
            'click .load_phy_appointment_today': 'load_phy_appointment_today',
            'click .load_pcr_appointment_today': 'load_pcr_appointment_today',
            'click .load_pcr_app': 'load_pcr_app',
            'click .load_pcr_app_opm': 'load_pcr_app_opm',
            'click .load_pcr_app_t': 'load_pcr_app_t',
            'click .load_pcr_all_appointment': 'load_pcr_all_appointment',
            'click .load_sleep_med': 'load_sleep_med',
            'click .load_notification': 'load_notification',
            'click .load_image_request': 'load_image_request',
            'click .load_lab_request': 'load_lab_request',
            'click .load_investigation_c': 'load_investigation_c',
            'click .load_referral': 'load_referral',
            'click .load_payment': 'load_payment',
            'click .load_paid_payment': 'load_paid_payment',
            'click .load_send_payment': 'load_send_payment',
            'click .load_cancellation_refund': 'load_cancellation_refund',
            'click .load_cancellation_op_refund': 'load_cancellation_op_refund',
            'click .load_cancellation_pr_refund': 'load_cancellation_pr_refund',
            'click .load_hhc_app_tod_res_the': 'load_hhc_app_tod_res_the',
            'click .load_tele_app_tod_res_the': 'load_tele_app_tod_res_the',
            'click .load_hhc_app_tod_soc_wor': 'load_hhc_app_tod_soc_wor',
            'click .load_tele_app_tod_soc_wor': 'load_tele_app_tod_soc_wor',
            'click .load_hhc_app_tod_hhc_nurse': 'load_hhc_app_tod_hhc_nurse',
            'click .load_tele_app_tod_hhc_nurse': 'load_tele_app_tod_hhc_nurse',
            'click .load_pcr_app_tod_hhc_nurse': 'load_pcr_app_tod_hhc_nurse',
            'click .load_pcr_app_tod_lab_technician': 'load_pcr_app_tod_lab_technician',
            'click .load_phy_app_tod_hhc_phy': 'load_phy_app_tod_hhc_phy',
            'click .load_hhc_app_tod_hhc_phy': 'load_hhc_app_tod_hhc_phy',
            'click .load_tele_app_tod_hhc_phy': 'load_tele_app_tod_hhc_phy',
            'click .load_tele_app_tod_tele_app': 'load_tele_app_tod_tele_app',
            'click .load_hhc_app_tod_hhc_doctor': 'load_hhc_app_tod_hhc_doctor',
            'click .load_tele_app_tod_hhc_doctor': 'load_tele_app_tod_hhc_doctor',
            'click .load_hvd_app_tod_hhc_doctor': 'load_hvd_app_tod_hhc_doctor',
            'click .load_tele_app_tod_head_phy': 'load_tele_app_tod_head_phy',
            'click .load_hhc_app_tod_head_phy': 'load_hhc_app_tod_head_phy',
            'click .load_phy_app_tod_head_phy': 'load_phy_app_tod_head_phy',
            'click .load_hhc_app_tod_head_nurse': 'load_hhc_app_tod_head_nurse',
            'click .load_pcr_app_tod_head_nurse': 'load_pcr_app_tod_head_nurse',
            'click .load_hvd_app_tod_head_doctor': 'load_hvd_app_tod_head_doctor',
            'click .load_hhc_app_tod_head_doctor': 'load_hhc_app_tod_head_doctor',
            'click .load_call_center': 'load_call_center',
            'click .load_call_center_op': 'load_call_center_op',
            'click .load_hhc_appointment_vd': 'load_hhc_appointment_vd',
            'click .load_hhc_appointment_inp': 'load_hhc_appointment_inp',
            'click .load_hhc_appointment_ca': 'load_hhc_appointment_ca',
            'click .load_web_req': 'load_web_req',
            // sleep medicine req
            'click .load_unpaid_slep_me_req': 'load_unpaid_slep_me_req',
            'click .load_paid_slep_me_req': 'load_paid_slep_me_req',
            'click .load_ev_slep_me_req': 'load_ev_slep_me_req',
            'click .load_sch_slep_me_req': 'load_sch_slep_me_req',
            // Caregiver Request
            'click .load_unpaid_car_cont': 'load_unpaid_car_cont',
            'click .load_paid_car_cont': 'load_paid_car_cont',
            'click .load_ev_car_cont': 'load_ev_car_cont',
            'click .load_car_cont_as_car': 'load_car_cont_as_car',
            'click .load_car_cont_act': 'load_car_cont_act',
            'click .load_car_cont_rea_req': 'load_car_cont_rea_req',

            'click .load_car_cont_hrq': 'load_car_cont_hrq',
            'click .load_car_cont_trq': 'load_car_cont_trq',
            'click .load_car_cont_rew': 'load_car_cont_rew',
            'click .load_car_cont_hol': 'load_car_cont_hol',
            'click .load_hhc_app_cr': 'load_hhc_app_cr',
            'click .load_phy_app_cr': 'load_phy_app_cr',
            'click .load_draft_payment': 'load_draft_payment',


            'click .load_lab_test': 'load_lab_test',
            'click .load_my_hhc_appointment': 'load_my_hhc_appointment',
            'click .load_patient': 'load_patient',
            'click .load_my_patient': 'load_my_patient',
            'click .load_physician': 'load_physician',
            'click .load_appointment': 'load_appointment',
            'click .load_my_appointment': 'load_my_appointment',
            'click .load_scheduled_apt': 'load_scheduled_apt',
            'click .load_invoice': 'load_invoice',
            'click .load_treatment': 'load_treatment',
            'click .load_my_treatment': 'load_my_treatment',


            'click #oeh_filter_btn_today': 'sm_filter_today',
            'click #oeh_filter_btn_week': 'sm_filter_week',
            'click #oeh_filter_btn_month': 'sm_filter_month',
            'click #oeh_filter_btn_now': 'sm_filter_now',
        },

        init: function (parent, context) {
            this._super(parent, context);
            // this.upcoming_events = [];
            this.dashboards_templates = ['smDashboardFilter', 'HealthCenterUser', 'HealthCenterAdmin'];
            this.login_employee = [];
        },

        willStart: function () {
            var self = this;
            this.login_employee = {};
            $('#oeh_curr_day_patient').addClass('d-none');
            $('#oeh_curr_week_patient').addClass('d-none');
            $('#oeh_curr_month_patient').addClass('d-none');
            $('#oeh_total_patient').addClass('d-none');
            return this._super().then(function () {

                var def0 = self._rpc({
                    model: 'sm.dashboard',
                    method: 'login_user_group'
                }).then(function (result) {
                    self.group_no = result;
                    //                 console.log(result)
                });
                return $.when(def0);
                // return $.when(def0, def1, def2, def3, def4, def5, def6, def7, def8, def9, def10, def11, def12, def13);
            });
        },

        sm_filter_today: function (ev) {
            var self = this;

            /* Filter */
            $('.oeh_dashboard_filter_btn .btn').each(function (e) {
                this.classList.remove('btn-success')
            })
            ev.currentTarget.classList.add('btn-success')

            /* Dashboard Data */
            rpc.query({
                model: 'sm.dashboard',
                method: 'sm_data_today',
                args: [],
            })
                .then(function (result) {

                    setCountValueToXml('.sm_total_ta', result.tele_app_ids.shift())
                    ids_tele_sch = result.tele_app_ids
                    setCountValueToXml('.sm_missed_medicines', result.missed_medicines_ids.shift())
                    ids_missed_medicine = result.missed_medicines_ids
                    setCountValueToXml('.sm_cancel_medicines', result.cancel_medicines_ids.shift())
                    ids_cancel_medicine = result.cancel_medicines_ids
                    setCountValueToXml('.sm_total_tac', result.tele_app_con_ids.shift())
                    ids_tele_con = result.tele_app_con_ids
                    setCountValueToXml('.sm_total_my_tele_sch_con', result.my_tele_sch_con_ids.shift())
                    ids_tele_sch_con = result.my_tele_sch_con_ids
                    setCountValueToXml('.sm_total_hvd', result.hvd_app_sch_ids.shift())
                    ids_hvd_sch = result.hvd_app_sch_ids
                    setCountValueToXml('.sm_total_hvd_c', result.hvd_app_con_ids.shift())
                    ids_hvd_con = result.hvd_app_con_ids
                    setCountValueToXml('.sm_total_my_hvd_sch_con', result.my_hvd_sch_con_ids.shift())
                    ids_hvd_sch_con = result.my_hvd_sch_con_ids
                    setCountValueToXml('.sm_total_phys', result.physiotherapy_app_sc_ids.shift())
                    ids_physiotherapy_sc = result.physiotherapy_app_sc_ids
                    setCountValueToXml('.sm_total_phys_hp', result.physiotherapy_app_co_ids.shift())
                    ids_physiotherapy_co = result.physiotherapy_app_co_ids
                    setCountValueToXml('.sm_total_phys_om', result.physiotherapy_app_op_ids.shift())
                    ids_physiotherapy_op = result.physiotherapy_app_op_ids
                    setCountValueToXml('.sm_total_phys_t', result.physiotherapy_app_tm_ids.shift())
                    ids_physiotherapy_tm = result.physiotherapy_app_tm_ids
                    setCountValueToXml('.sm_total_my_phy_all', result.my_phy_all_ids.shift())
                    ids_phy_all = result.my_phy_all_ids
                    setCountValueToXml('.sm_total_hhc', result.hhc_app_sch_ids.shift())
                    ids_hhc_sch = result.hhc_app_sch_ids
                    setCountValueToXml('.sm_total_hhc_c', result.hhc_app_hd_ids.shift())
                    ids_hhc_hd = result.hhc_app_hd_ids
                    setCountValueToXml('.sm_total_hhc_hn', result.hhc_app_hn_ids.shift())
                    ids_hhc_hn = result.hhc_app_hn_ids
                    setCountValueToXml('.sm_total_hhc_om', result.hhc_app_om_ids.shift())
                    ids_hhc_om = result.hhc_app_om_ids
                    setCountValueToXml('.sm_total_hhc_t', result.hhc_app_tm_ids.shift())
                    ids_hhc_tm = result.hhc_app_tm_ids
                    setCountValueToXml('.sm_total_my_hhc_all', result.my_hhc_sch_all_ids.shift())
                    ids_hhc_all = result.my_hhc_sch_all_ids
                    setCountValueToXml('.sm_total_my_tele_tod', result.my_tele_today_ids.shift())
                    ids_tele_today = result.my_tele_today_ids
                    setCountValueToXml('.sm_total_my_hvd_tod', result.my_hvd_today_ids.shift())
                    ids_hvd_today = result.my_hvd_today_ids
                    setCountValueToXml('.sm_total_my_hhc_tod', result.my_hhc_today_ids.shift())
                    ids_hhc_today = result.my_hhc_today_ids
                    setCountValueToXml('.sm_total_my_phy_tod', result.my_phy_today_ids.shift())
                    ids_phy_today = result.my_phy_today_ids
                    setCountValueToXml('.sm_total_my_pcr_tod', result.my_pcr_today_ids.shift())
                    ids_pcr_today = result.my_pcr_today_ids
                    setCountValueToXml('.sm_total_pcr_app', result.pcr_app_sch_ids.shift())
                    ids_pcr_sch = result.pcr_app_sch_ids
                    setCountValueToXml('.sm_total_pcr_opm', result.pcr_app_opm_ids.shift())
                    ids_pcr_opm = result.pcr_app_opm_ids
                    setCountValueToXml('.sm_total_pcr_app_team', result.pcr_app_tm_ids.shift())
                    ids_pcr_tm = result.pcr_app_tm_ids
                    setCountValueToXml('.sm_total_my_pcr_all', result.my_pcr_all_ids.shift())
                    ids_pcr_all = result.my_pcr_all_ids
                    setCountValueToXml('.oeh_total_service_request', result.service_request_ids.shift())
                    ids_ser_req = result.service_request_ids
                    setCountValueToXml('.oeh_total_notification', result.notification_ids.shift())
                    ids_not = result.notification_ids
                    setCountValueToXml('.sm_total_image_request', result.image_request_ids.shift())
                    ids_image_req = result.image_request_ids
                    setCountValueToXml('.sm_total_lab_request', result.lab_request_ids.shift())
                    ids_lab_rec = result.lab_request_ids
                    setCountValueToXml('.sm_total_investigation', result.investigation_ids.shift())
                    ids_inve = result.investigation_ids
                    setCountValueToXml('.oeh_total_referral', result.referral_ids.shift())
                    ids_ref = result.referral_ids
                    setCountValueToXml('.sm_total_payment', result.requested_payments_ids.shift())
                    ids_payments = result.requested_payments_ids
                    setCountValueToXml('.sm_total_send_payment', result.requested_payments_send_ids.shift())
                    ids_send_payments = result.requested_payments_send_ids
                    setCountValueToXml('.sm_total_paid_payment', result.requested_payments_paid_ids.shift())
                    ids_paid_payment = result.requested_payments_paid_ids
                    setCountValueToXml('.sm_total_cancellation_refund', result.cancellation_refund_ids.shift())
                    ids_cancellation = result.cancellation_refund_ids
                    setCountValueToXml('.sm_total_cancellation_refund_op', result.cancellation_refund_op_ids.shift())
                    ids_op_cancellation = result.cancellation_refund_op_ids
                    setCountValueToXml('.sm_total_cancellation_refund_pr', result.cancellation_refund_pr_ids.shift())
                    ids_pr_cancellation = result.cancellation_refund_pr_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_res_the', result.hhc_tod_tm_res_the_ids.shift())
                    ids_hhc_tod_tm_res_the = result.hhc_tod_tm_res_the_ids
                    setCountValueToXml('.sm_total_tele_tod_tm_res_the', result.tele_tod_tm_res_the_ids.shift())
                    ids_tele_tod_tm_res_the = result.tele_tod_tm_res_the_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_soc_wor', result.hhc_tod_tm_soc_wor_ids.shift())
                    ids_hhc_tod_tm_soc_wor = result.hhc_tod_tm_soc_wor_ids
                    setCountValueToXml('.sm_total_tele_tod_con_soc_wor', result.tele_tod_con_soc_wor_ids.shift())
                    ids_tele_tod_con_soc_wor = result.tele_tod_con_soc_wor_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_hhc_nurse', result.hhc_tod_tm_hhc_nurse_ids.shift())
                    ids_hhc_tod_tm_hhc_nurse = result.hhc_tod_tm_hhc_nurse_ids
                    setCountValueToXml('.sm_total_tele_tod_con_hhc_nurse', result.tele_tod_con_hhc_nurse_ids.shift())
                    ids_tele_tod_con_hhc_nurse = result.tele_tod_con_hhc_nurse_ids
                    setCountValueToXml('.sm_total_pcr_tod_tm_hhc_nurse', result.pcr_tod_tm_hhc_nurse_ids.shift())
                    ids_pcr_tod_team_hhc_nurse = result.pcr_tod_tm_hhc_nurse_ids
                    setCountValueToXml('.sm_total_pcr_tod_tm_lab_technician', result.pcr_tod_tm_lab_technician_ids.shift())
                    ids_pcr_tod_team_lab_technician = result.pcr_tod_tm_lab_technician_ids
                    setCountValueToXml('.sm_total_phy_tod_tm_hhc_phy', result.phy_tod_tm_hhc_phy_ids.shift())
                    ids_phy_tod_team_hhc_phy = result.phy_tod_tm_hhc_phy_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_hhc_phy', result.hhc_tod_tm_hhc_phy_ids.shift())
                    ids_hhc_tod_team_hhc_phy = result.hhc_tod_tm_hhc_phy_ids
                    setCountValueToXml('.sm_total_tele_tod_con_hhc_phy', result.tele_tod_con_hhc_phy_ids.shift())
                    ids_tele_tod_con_hhc_phy = result.tele_tod_con_hhc_phy_ids
                    setCountValueToXml('.sm_total_tele_tod_con_tele_app', result.tele_tod_con_tele_app_ids.shift())
                    ids_tele_tod_con_tele_app = result.tele_tod_con_tele_app_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_hhc_doctor', result.hhc_tod_tm_hhc_doctor_ids.shift())
                    ids_hhc_tod_team_hhc_doctor = result.hhc_tod_tm_hhc_doctor_ids
                    setCountValueToXml('.sm_total_tele_tod_con_hhc_doctor', result.tele_tod_con_hhc_doctor_ids.shift())
                    ids_tele_tod_con_hhc_doctor = result.tele_tod_con_hhc_doctor_ids
                    setCountValueToXml('.sm_total_hvd_tod_con_hhc_doctor', result.hvd_tod_con_hhc_doctor_ids.shift())
                    ids_hvd_tod_con_hhc_doctor = result.hvd_tod_con_hhc_doctor_ids
                    setCountValueToXml('.sm_total_tele_tod_con_head_phy', result.tele_tod_con_head_phy_ids.shift())
                    ids_tele_tod_con_head_phy = result.tele_tod_con_head_phy_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_head_phy', result.hhc_tod_tm_head_phy_ids.shift())
                    ids_hhc_tod_tm_head_phy = result.hhc_tod_tm_head_phy_ids
                    setCountValueToXml('.sm_total_phy_tod_tm_head_phy', result.phy_tod_tm_head_phy_ids.shift())
                    ids_phy_tod_tm_head_phy = result.phy_tod_tm_head_phy_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_head_nurse', result.hhc_tod_tm_head_nurse_ids.shift())
                    ids_hhc_tod_tm_head_nurse = result.hhc_tod_tm_head_nurse_ids
                    setCountValueToXml('.sm_total_pcr_tod_tm_head_nurse', result.pcr_tod_tm_head_nurse_ids.shift())
                    ids_pcr_tod_tm_head_nurse = result.pcr_tod_tm_head_nurse_ids
                    setCountValueToXml('.sm_total_hvd_tod_con_head_doctor', result.hvd_tod_con_head_doctor_ids.shift())
                    ids_hvd_tod_con_head_doctor = result.hvd_tod_con_head_doctor_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_head_doctor', result.hhc_tod_tm_head_doctor_ids.shift())
                    ids_hhc_tod_tm_head_doctor = result.hhc_tod_tm_head_doctor_ids
                    setCountValueToXml('.sm_total_call_center', result.call_center_ids.shift())
                    ids_call_center = result.call_center_ids
                    setCountValueToXml('.sm_total_call_center_op', result.call_center_op_ids.shift())
                    ids_call_center_op = result.call_center_op_ids
                    setCountValueToXml('.sm_total_hhc_vd', result.hhc_app_vd_ids.shift())
                    ids_hhc_vd = result.hhc_app_vd_ids
                    setCountValueToXml('.sm_total_hhc_inp', result.hhc_app_inp_ids.shift())
                    ids_hhc_inp = result.hhc_app_inp_ids
                    setCountValueToXml('.sm_total_hhc_ca', result.hhc_app_ca_ids.shift())
                    ids_hhc_ca = result.hhc_app_ca_ids
                    setCountValueToXml('.sm_total_web_req', result.web_req_ids.shift())
                    ids_web_req = result.web_req_ids
                    setCountValueToXml('.sm_total_phys_inp', result.physiotherapy_app_inp_ids.shift())
                    ids_physiotherapy_inp = result.physiotherapy_app_inp_ids
                    setCountValueToXml('.sm_total_phys_vd', result.physiotherapy_app_vd_ids.shift())
                    ids_physiotherapy_vd = result.physiotherapy_app_vd_ids
                    setCountValueToXml('.sm_total_phys_ca', result.physiotherapy_app_ca_ids.shift())
                    ids_physiotherapy_ca = result.physiotherapy_app_ca_ids





                    setCountValueToXml('.sm_total_my_hhc_t', result.my_hhc_app_tm_ids.shift())
                    ids_my_hhc_app_tem = result.my_hhc_app_tm_ids
                    setCountValueToXml('.sm_total_my_hhc_phy_tem', result.my_hhc_app_phy_tm_ids.shift())
                    ids_my_hhc_app_phys_tem = result.my_hhc_app_phy_tm_ids
                    setCountValueToXml('.sm_total_my_phys_t', result.my_physiotherapy_app_tm_ids.shift())
                    ids_my_physiotherapy_app_tem = result.my_physiotherapy_app_tm_ids
                    //                console.log(result.my_physiotherapy_app_sch_ids)
                    setCountValueToXml('.sm_total_my_phys_sch', result.my_physiotherapy_app_sch_ids.shift())
                    ids_my_physiotherapy_app_sch = result.my_physiotherapy_app_sch_ids
                    setCountValueToXml('.sm_total_my_phys_hp', result.my_physiotherapy_app_hp_ids.shift())
                    ids_my_physiotherapy_app_hp = result.my_physiotherapy_app_hp_ids
                    setCountValueToXml('.sm_total_my_phys_op', result.my_physiotherapy_app_op_ids.shift())
                    ids_my_physiotherapy_app_op = result.my_physiotherapy_app_op_ids
                    setCountValueToXml('.sm_total_my_h_hhc_t', result.my_h_hhc_app_tm_ids.shift())
                    ids_my_h_hhc_app_tem = result.my_h_hhc_app_tm_ids
                    setCountValueToXml('.sm_total_my_tac', result.my_tele_app_con_ids.shift())
                    ids_my_tele_con = result.my_tele_app_con_ids
                    setCountValueToXml('.sm_total_my_hvd_c', result.my_hvd_app_con_ids.shift())
                    ids_my_hvd_con = result.my_hvd_app_con_ids
                    setCountValueToXml('.sm_total_my_hn_tac', result.my_tele_app_hn_con_ids.shift())
                    ids_my_hn_tele_con = result.my_tele_app_hn_con_ids
                    setCountValueToXml('.sm_total_my_hdphy_tac', result.my_tele_app_hdphy_con_ids.shift())
                    ids_my_hdphy_tele_con = result.my_tele_app_hdphy_con_ids
                    setCountValueToXml('.sm_total_my_hhcn_tac', result.my_tele_app_hhcn_con_ids.shift())
                    ids_my_hhcn_tele_con = result.my_tele_app_hhcn_con_ids
                    setCountValueToXml('.sm_total_my_hhcn_pcr', result.my_hhcn_pcr_app_tm_ids.shift())
                    ids_my_hhcn_pcr_con = result.my_hhcn_pcr_app_tm_ids
                    setCountValueToXml('.sm_total_my_hhphy_tele', result.my_tele_app_hhcphy_con_ids.shift())
                    ids_my_hhcphy_pcr_con = result.my_tele_app_hhcphy_con_ids
                    setCountValueToXml('.sm_total_my_rh_hhc_t', result.my_rh_hhc_app_tm_ids.shift())
                    ids_my_rh_hhc_app_tem = result.my_rh_hhc_app_tm_ids
                    setCountValueToXml('.sm_total_my_rh_tac', result.my_rh_tele_app_con_ids.shift())
                    ids_my_rh_tele_con = result.my_rh_tele_app_con_ids
                    setCountValueToXml('.sm_total_my_rh_hvd_c', result.my_rh_hvd_app_con_ids.shift())
                    ids_my_rh_hvd_con = result.my_rh_hvd_app_con_ids
                    // Sleep Medicine Request
                    setCountValueToXml('.sm_total_slep_me_req_unpaid', result.slep_me_req_unpaid_ids.shift())
                    ids_slep_me_req_unpaid = result.slep_me_req_unpaid_ids

                    setCountValueToXml('.sm_total_slep_me_req_paid', result.slep_me_req_paid_ids.shift())
                    ids_slep_me_req_paid = result.slep_me_req_paid_ids

                    setCountValueToXml('.sm_total_slep_me_req_ev', result.slep_me_req_ev_ids.shift())
                    ids_slep_me_req_ev = result.slep_me_req_ev_ids

                    setCountValueToXml('.sm_total_slep_me_req_sch', result.slep_me_req_sch_ids.shift())
                    ids_slep_me_req_sch = result.slep_me_req_sch_ids
                    // Caregiver Contract
                    setCountValueToXml('.sm_total_car_cont_unpaid', result.car_cont_unpaid_ids.shift())
                    ids_car_cont_unpaid = result.car_cont_unpaid_ids
                    setCountValueToXml('.sm_total_car_cont_paid', result.car_cont_paid_ids.shift())
                    ids_car_cont_paid = result.car_cont_paid_ids

                    setCountValueToXml('.sm_total_car_cont_ev', result.car_cont_ev_ids.shift())
                    ids_car_cont_ev = result.car_cont_ev_ids
                    setCountValueToXml('.sm_total_car_cont_as_car', result.car_cont_as_car_ids.shift())
                    ids_car_cont_as_car = result.car_cont_as_car_ids
                    setCountValueToXml('.sm_total_car_cont_act', result.car_cont_act_ids.shift())
                    ids_car_cont_act = result.car_cont_act_ids

                    setCountValueToXml('.sm_total_car_cont_rea_req', result.car_cont_rea_req_ids.shift())
                    ids_car_cont_rea_req = result.car_cont_rea_req_ids

                    setCountValueToXml('.sm_total_car_cont_hrq', result.car_cont_hrq_ids.shift())
                    ids_car_cont_hrq = result.car_cont_hrq_ids
                    setCountValueToXml('.sm_total_car_cont_trq', result.car_cont_trq_ids.shift())
                    ids_car_cont_trq = result.car_cont_trq_ids
                    setCountValueToXml('.sm_total_car_cont_rew', result.car_cont_rew_ids.shift())
                    ids_car_cont_rew = result.car_cont_rew_ids
                    setCountValueToXml('.sm_total_car_cont_hol', result.car_cont_hol_ids.shift())
                    ids_car_cont_hol = result.car_cont_hol_ids

                    setCountValueToXml('.sm_total_hhc_app_cr', result.hhc_app_cr_ids.shift())
                    ids_hhc_app_cr = result.hhc_app_cr_ids
                    setCountValueToXml('.sm_total_phy_app_cr', result.phy_app_cr_ids.shift())
                    ids_phy_app_cr = result.phy_app_cr_ids

                    setCountValueToXml('.sm_total_draft_payment', result.draft_payment_ids.shift())
                    ids_draft_payment = result.draft_payment_ids

                })
        },

        sm_filter_week: function (ev) {
            var self = this;
            /* Filter */
            $('.oeh_dashboard_filter_btn .btn').each(function (e) {
                this.classList.remove('btn-success')
            })
            ev.currentTarget.classList.add('btn-success')

            /* Dashboard Data */
            rpc.query({
                model: 'sm.dashboard',
                method: 'sm_data_week',
                args: [],
            })
                .then(function (result) {

                    setCountValueToXml('.sm_total_ta', result.tele_app_ids.shift())
                    ids_tele_sch = result.tele_app_ids
                    setCountValueToXml('.sm_missed_medicines', result.missed_medicines_ids.shift())
                    ids_missed_medicine = result.missed_medicines_ids
                    setCountValueToXml('.sm_cancel_medicines', result.cancel_medicines_ids.shift())
                    ids_cancel_medicine = result.cancel_medicines_ids
                    setCountValueToXml('.sm_total_tac', result.tele_app_con_ids.shift())
                    ids_tele_con = result.tele_app_con_ids
                    setCountValueToXml('.sm_total_my_tele_sch_con', result.my_tele_sch_con_ids.shift())
                    ids_tele_sch_con = result.my_tele_sch_con_ids
                    setCountValueToXml('.sm_total_hvd', result.hvd_app_sch_ids.shift())
                    ids_hvd_sch = result.hvd_app_sch_ids
                    setCountValueToXml('.sm_total_hvd_c', result.hvd_app_con_ids.shift())
                    ids_hvd_con = result.hvd_app_con_ids
                    setCountValueToXml('.sm_total_my_hvd_sch_con', result.my_hvd_sch_con_ids.shift())
                    ids_hvd_sch_con = result.my_hvd_sch_con_ids
                    setCountValueToXml('.sm_total_phys', result.physiotherapy_app_sc_ids.shift())
                    ids_physiotherapy_sc = result.physiotherapy_app_sc_ids
                    setCountValueToXml('.sm_total_phys_hp', result.physiotherapy_app_co_ids.shift())
                    ids_physiotherapy_co = result.physiotherapy_app_co_ids
                    setCountValueToXml('.sm_total_phys_om', result.physiotherapy_app_op_ids.shift())
                    ids_physiotherapy_op = result.physiotherapy_app_op_ids
                    setCountValueToXml('.sm_total_phys_t', result.physiotherapy_app_tm_ids.shift())
                    ids_physiotherapy_tm = result.physiotherapy_app_tm_ids
                    setCountValueToXml('.sm_total_my_phy_all', result.my_phy_all_ids.shift())
                    ids_phy_all = result.my_phy_all_ids
                    setCountValueToXml('.sm_total_hhc', result.hhc_app_sch_ids.shift())
                    ids_hhc_sch = result.hhc_app_sch_ids
                    setCountValueToXml('.sm_total_hhc_c', result.hhc_app_hd_ids.shift())
                    ids_hhc_hd = result.hhc_app_hd_ids
                    setCountValueToXml('.sm_total_hhc_hn', result.hhc_app_hn_ids.shift())
                    ids_hhc_hn = result.hhc_app_hn_ids
                    setCountValueToXml('.sm_total_hhc_om', result.hhc_app_om_ids.shift())
                    ids_hhc_om = result.hhc_app_om_ids
                    setCountValueToXml('.sm_total_hhc_t', result.hhc_app_tm_ids.shift())
                    ids_hhc_tm = result.hhc_app_tm_ids
                    setCountValueToXml('.sm_total_my_hhc_all', result.my_hhc_sch_all_ids.shift())
                    ids_hhc_all = result.my_hhc_sch_all_ids
                    setCountValueToXml('.sm_total_my_tele_tod', result.my_tele_today_ids.shift())
                    ids_tele_today = result.my_tele_today_ids
                    setCountValueToXml('.sm_total_my_hvd_tod', result.my_hvd_today_ids.shift())
                    ids_hvd_today = result.my_hvd_today_ids
                    setCountValueToXml('.sm_total_my_hhc_tod', result.my_hhc_today_ids.shift())
                    ids_hhc_today = result.my_hhc_today_ids
                    setCountValueToXml('.sm_total_my_phy_tod', result.my_phy_today_ids.shift())
                    ids_phy_today = result.my_phy_today_ids
                    setCountValueToXml('.sm_total_my_pcr_tod', result.my_pcr_today_ids.shift())
                    ids_pcr_today = result.my_pcr_today_ids
                    setCountValueToXml('.sm_total_pcr_app', result.pcr_app_sch_ids.shift())
                    ids_pcr_sch = result.pcr_app_sch_ids
                    setCountValueToXml('.sm_total_pcr_opm', result.pcr_app_opm_ids.shift())
                    ids_pcr_opm = result.pcr_app_opm_ids
                    setCountValueToXml('.sm_total_pcr_app_team', result.pcr_app_tm_ids.shift())
                    ids_pcr_tm = result.pcr_app_tm_ids
                    setCountValueToXml('.sm_total_my_pcr_all', result.my_pcr_all_ids.shift())
                    ids_pcr_all = result.my_pcr_all_ids
                    setCountValueToXml('.oeh_total_service_request', result.service_request_ids.shift())
                    ids_ser_req = result.service_request_ids
                    setCountValueToXml('.oeh_total_notification', result.notification_ids.shift())
                    ids_not = result.notification_ids
                    setCountValueToXml('.sm_total_image_request', result.image_request_ids.shift())
                    ids_image_req = result.image_request_ids
                    setCountValueToXml('.sm_total_lab_request', result.lab_request_ids.shift())
                    ids_lab_rec = result.lab_request_ids
                    setCountValueToXml('.sm_total_investigation', result.investigation_ids.shift())
                    ids_inve = result.investigation_ids
                    setCountValueToXml('.oeh_total_referral', result.referral_ids.shift())
                    ids_ref = result.referral_ids
                    setCountValueToXml('.sm_total_payment', result.requested_payments_ids.shift())
                    ids_payments = result.requested_payments_ids
                    setCountValueToXml('.sm_total_send_payment', result.requested_payments_send_ids.shift())
                    ids_send_payments = result.requested_payments_send_ids
                    setCountValueToXml('.sm_total_paid_payment', result.requested_payments_paid_ids.shift())
                    ids_paid_payment = result.requested_payments_paid_ids
                    setCountValueToXml('.sm_total_cancellation_refund', result.cancellation_refund_ids.shift())
                    ids_cancellation = result.cancellation_refund_ids
                    setCountValueToXml('.sm_total_cancellation_refund_op', result.cancellation_refund_op_ids.shift())
                    ids_op_cancellation = result.cancellation_refund_op_ids
                    setCountValueToXml('.sm_total_cancellation_refund_pr', result.cancellation_refund_pr_ids.shift())
                    ids_pr_cancellation = result.cancellation_refund_pr_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_res_the', result.hhc_tod_tm_res_the_ids.shift())
                    ids_hhc_tod_tm_res_the = result.hhc_tod_tm_res_the_ids
                    setCountValueToXml('.sm_total_tele_tod_tm_res_the', result.tele_tod_tm_res_the_ids.shift())
                    ids_tele_tod_tm_res_the = result.tele_tod_tm_res_the_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_soc_wor', result.hhc_tod_tm_soc_wor_ids.shift())
                    ids_hhc_tod_tm_soc_wor = result.hhc_tod_tm_soc_wor_ids
                    setCountValueToXml('.sm_total_tele_tod_con_soc_wor', result.tele_tod_con_soc_wor_ids.shift())
                    ids_tele_tod_con_soc_wor = result.tele_tod_con_soc_wor_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_hhc_nurse', result.hhc_tod_tm_hhc_nurse_ids.shift())
                    ids_hhc_tod_tm_hhc_nurse = result.hhc_tod_tm_hhc_nurse_ids
                    setCountValueToXml('.sm_total_tele_tod_con_hhc_nurse', result.tele_tod_con_hhc_nurse_ids.shift())
                    ids_tele_tod_con_hhc_nurse = result.tele_tod_con_hhc_nurse_ids
                    setCountValueToXml('.sm_total_pcr_tod_tm_hhc_nurse', result.pcr_tod_tm_hhc_nurse_ids.shift())
                    ids_pcr_tod_team_hhc_nurse = result.pcr_tod_tm_hhc_nurse_ids
                    setCountValueToXml('.sm_total_pcr_tod_tm_lab_technician', result.pcr_tod_tm_lab_technician_ids.shift())
                    ids_pcr_tod_team_lab_technician = result.pcr_tod_tm_lab_technician_ids
                    setCountValueToXml('.sm_total_phy_tod_tm_hhc_phy', result.phy_tod_tm_hhc_phy_ids.shift())
                    ids_phy_tod_team_hhc_phy = result.phy_tod_tm_hhc_phy_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_hhc_phy', result.hhc_tod_tm_hhc_phy_ids.shift())
                    ids_hhc_tod_team_hhc_phy = result.hhc_tod_tm_hhc_phy_ids
                    setCountValueToXml('.sm_total_tele_tod_con_hhc_phy', result.tele_tod_con_hhc_phy_ids.shift())
                    ids_tele_tod_con_hhc_phy = result.tele_tod_con_hhc_phy_ids
                    setCountValueToXml('.sm_total_tele_tod_con_tele_app', result.tele_tod_con_tele_app_ids.shift())
                    ids_tele_tod_con_tele_app = result.tele_tod_con_tele_app_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_hhc_doctor', result.hhc_tod_tm_hhc_doctor_ids.shift())
                    ids_hhc_tod_team_hhc_doctor = result.hhc_tod_tm_hhc_doctor_ids
                    setCountValueToXml('.sm_total_tele_tod_con_hhc_doctor', result.tele_tod_con_hhc_doctor_ids.shift())
                    ids_tele_tod_con_hhc_doctor = result.tele_tod_con_hhc_doctor_ids
                    setCountValueToXml('.sm_total_hvd_tod_con_hhc_doctor', result.hvd_tod_con_hhc_doctor_ids.shift())
                    ids_hvd_tod_con_hhc_doctor = result.hvd_tod_con_hhc_doctor_ids
                    setCountValueToXml('.sm_total_tele_tod_con_head_phy', result.tele_tod_con_head_phy_ids.shift())
                    ids_tele_tod_con_head_phy = result.tele_tod_con_head_phy_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_head_phy', result.hhc_tod_tm_head_phy_ids.shift())
                    ids_hhc_tod_tm_head_phy = result.hhc_tod_tm_head_phy_ids
                    setCountValueToXml('.sm_total_phy_tod_tm_head_phy', result.phy_tod_tm_head_phy_ids.shift())
                    ids_phy_tod_tm_head_phy = result.phy_tod_tm_head_phy_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_head_nurse', result.hhc_tod_tm_head_nurse_ids.shift())
                    ids_hhc_tod_tm_head_nurse = result.hhc_tod_tm_head_nurse_ids
                    setCountValueToXml('.sm_total_pcr_tod_tm_head_nurse', result.pcr_tod_tm_head_nurse_ids.shift())
                    ids_pcr_tod_tm_head_nurse = result.pcr_tod_tm_head_nurse_ids
                    setCountValueToXml('.sm_total_hvd_tod_con_head_doctor', result.hvd_tod_con_head_doctor_ids.shift())
                    ids_hvd_tod_con_head_doctor = result.hvd_tod_con_head_doctor_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_head_doctor', result.hhc_tod_tm_head_doctor_ids.shift())
                    ids_hhc_tod_tm_head_doctor = result.hhc_tod_tm_head_doctor_ids
                    setCountValueToXml('.sm_total_call_center', result.call_center_ids.shift())
                    ids_call_center = result.call_center_ids
                    setCountValueToXml('.sm_total_call_center_op', result.call_center_op_ids.shift())
                    ids_call_center_op = result.call_center_op_ids
                    setCountValueToXml('.sm_total_hhc_vd', result.hhc_app_vd_ids.shift())
                    ids_hhc_vd = result.hhc_app_vd_ids
                    setCountValueToXml('.sm_total_hhc_inp', result.hhc_app_inp_ids.shift())
                    ids_hhc_inp = result.hhc_app_inp_ids
                    setCountValueToXml('.sm_total_hhc_ca', result.hhc_app_ca_ids.shift())
                    ids_hhc_ca = result.hhc_app_ca_ids
                    setCountValueToXml('.sm_total_web_req', result.web_req_ids.shift())
                    ids_web_req = result.web_req_ids
                    setCountValueToXml('.sm_total_phys_inp', result.physiotherapy_app_inp_ids.shift())
                    ids_physiotherapy_inp = result.physiotherapy_app_inp_ids
                    setCountValueToXml('.sm_total_phys_vd', result.physiotherapy_app_vd_ids.shift())
                    ids_physiotherapy_vd = result.physiotherapy_app_vd_ids
                    setCountValueToXml('.sm_total_phys_ca', result.physiotherapy_app_ca_ids.shift())
                    ids_physiotherapy_ca = result.physiotherapy_app_ca_ids





                    setCountValueToXml('.sm_total_my_hhc_t', result.my_hhc_app_tm_ids.shift())
                    ids_my_hhc_app_tem = result.my_hhc_app_tm_ids
                    setCountValueToXml('.sm_total_my_hhc_phy_tem', result.my_hhc_app_phy_tm_ids.shift())
                    ids_my_hhc_app_phys_tem = result.my_hhc_app_phy_tm_ids
                    setCountValueToXml('.sm_total_my_phys_t', result.my_physiotherapy_app_tm_ids.shift())
                    ids_my_physiotherapy_app_tem = result.my_physiotherapy_app_tm_ids
                    setCountValueToXml('.sm_total_my_phys_sch', result.my_physiotherapy_app_sch_ids.shift())
                    ids_my_physiotherapy_app_sch = result.my_physiotherapy_app_sch_ids
                    setCountValueToXml('.sm_total_my_phys_hp', result.my_physiotherapy_app_hp_ids.shift())
                    ids_my_physiotherapy_app_hp = result.my_physiotherapy_app_hp_ids
                    setCountValueToXml('.sm_total_my_phys_op', result.my_physiotherapy_app_op_ids.shift())
                    ids_my_physiotherapy_app_op = result.my_physiotherapy_app_op_ids
                    setCountValueToXml('.sm_total_my_h_hhc_t', result.my_h_hhc_app_tm_ids.shift())
                    ids_my_h_hhc_app_tem = result.my_h_hhc_app_tm_ids
                    setCountValueToXml('.sm_total_my_tac', result.my_tele_app_con_ids.shift())
                    ids_my_tele_con = result.my_tele_app_con_ids
                    setCountValueToXml('.sm_total_my_hvd_c', result.my_hvd_app_con_ids.shift())
                    ids_my_hvd_con = result.my_hvd_app_con_ids
                    setCountValueToXml('.sm_total_my_hn_tac', result.my_tele_app_hn_con_ids.shift())
                    ids_my_hn_tele_con = result.my_tele_app_hn_con_ids
                    setCountValueToXml('.sm_total_my_hdphy_tac', result.my_tele_app_hdphy_con_ids.shift())
                    ids_my_hdphy_tele_con = result.my_tele_app_hdphy_con_ids
                    setCountValueToXml('.sm_total_my_hhcn_tac', result.my_tele_app_hhcn_con_ids.shift())
                    ids_my_hhcn_tele_con = result.my_tele_app_hhcn_con_ids
                    setCountValueToXml('.sm_total_my_hhcn_pcr', result.my_hhcn_pcr_app_tm_ids.shift())
                    ids_my_hhcn_pcr_con = result.my_hhcn_pcr_app_tm_ids
                    setCountValueToXml('.sm_total_my_hhphy_tele', result.my_tele_app_hhcphy_con_ids.shift())
                    ids_my_hhcphy_pcr_con = result.my_tele_app_hhcphy_con_ids
                    setCountValueToXml('.sm_total_my_rh_hhc_t', result.my_rh_hhc_app_tm_ids.shift())
                    ids_my_rh_hhc_app_tem = result.my_rh_hhc_app_tm_ids
                    setCountValueToXml('.sm_total_my_rh_tac', result.my_rh_tele_app_con_ids.shift())
                    ids_my_rh_tele_con = result.my_rh_tele_app_con_ids
                    setCountValueToXml('.sm_total_my_rh_hvd_c', result.my_rh_hvd_app_con_ids.shift())
                    ids_my_rh_hvd_con = result.my_rh_hvd_app_con_ids
                    // Sleep Medicine Request
                    setCountValueToXml('.sm_total_slep_me_req_unpaid', result.slep_me_req_unpaid_ids.shift())
                    ids_slep_me_req_unpaid = result.slep_me_req_unpaid_ids

                    setCountValueToXml('.sm_total_slep_me_req_paid', result.slep_me_req_paid_ids.shift())
                    ids_slep_me_req_paid = result.slep_me_req_paid_ids

                    setCountValueToXml('.sm_total_slep_me_req_ev', result.slep_me_req_ev_ids.shift())
                    ids_slep_me_req_ev = result.slep_me_req_ev_ids

                    setCountValueToXml('.sm_total_slep_me_req_sch', result.slep_me_req_sch_ids.shift())
                    ids_slep_me_req_sch = result.slep_me_req_sch_ids
                    // Caregiver Contract
                    setCountValueToXml('.sm_total_car_cont_unpaid', result.car_cont_unpaid_ids.shift())
                    ids_car_cont_unpaid = result.car_cont_unpaid_ids
                    setCountValueToXml('.sm_total_car_cont_paid', result.car_cont_paid_ids.shift())
                    ids_car_cont_paid = result.car_cont_paid_ids

                    setCountValueToXml('.sm_total_car_cont_ev', result.car_cont_ev_ids.shift())
                    ids_car_cont_ev = result.car_cont_ev_ids
                    setCountValueToXml('.sm_total_car_cont_as_car', result.car_cont_as_car_ids.shift())
                    ids_car_cont_as_car = result.car_cont_as_car_ids
                    setCountValueToXml('.sm_total_car_cont_act', result.car_cont_act_ids.shift())
                    ids_car_cont_act = result.car_cont_act_ids

                    setCountValueToXml('.sm_total_car_cont_rea_req', result.car_cont_rea_req_ids.shift())
                    ids_car_cont_rea_req = result.car_cont_rea_req_ids

                    setCountValueToXml('.sm_total_car_cont_hrq', result.car_cont_hrq_ids.shift())
                    ids_car_cont_hrq = result.car_cont_hrq_ids
                    setCountValueToXml('.sm_total_car_cont_trq', result.car_cont_trq_ids.shift())
                    ids_car_cont_trq = result.car_cont_trq_ids
                    setCountValueToXml('.sm_total_car_cont_rew', result.car_cont_rew_ids.shift())
                    ids_car_cont_rew = result.car_cont_rew_ids
                    setCountValueToXml('.sm_total_car_cont_hol', result.car_cont_hol_ids.shift())
                    ids_car_cont_hol = result.car_cont_hol_ids

                    setCountValueToXml('.sm_total_hhc_app_cr', result.hhc_app_cr_ids.shift())
                    ids_hhc_app_cr = result.hhc_app_cr_ids
                    setCountValueToXml('.sm_total_phy_app_cr', result.phy_app_cr_ids.shift())
                    ids_phy_app_cr = result.phy_app_cr_ids

                    setCountValueToXml('.sm_total_draft_payment', result.draft_payment_ids.shift())
                    ids_draft_payment = result.draft_payment_ids

                })
        },

        sm_filter_month: function (ev) {
            var self = this;

            /* Filter */
            $('.oeh_dashboard_filter_btn .btn').each(function (e) {
                this.classList.remove('btn-success')
            })
            ev.currentTarget.classList.add('btn-success')

            /* Dashboard Data */
            rpc.query({
                model: 'sm.dashboard',
                method: 'sm_data_month',
                args: [],
            })
                .then(function (result) {

                    setCountValueToXml('.sm_total_ta', result.tele_app_ids.shift())
                    ids_tele_sch = result.tele_app_ids
                    setCountValueToXml('.sm_missed_medicines', result.missed_medicines_ids.shift())
                    ids_missed_medicine = result.missed_medicines_ids
                    setCountValueToXml('.sm_cancel_medicines', result.cancel_medicines_ids.shift())
                    ids_cancel_medicine = result.cancel_medicines_ids
                    setCountValueToXml('.sm_total_tac', result.tele_app_con_ids.shift())
                    ids_tele_con = result.tele_app_con_ids
                    setCountValueToXml('.sm_total_my_tele_sch_con', result.my_tele_sch_con_ids.shift())
                    ids_tele_sch_con = result.my_tele_sch_con_ids
                    setCountValueToXml('.sm_total_hvd', result.hvd_app_sch_ids.shift())
                    ids_hvd_sch = result.hvd_app_sch_ids
                    setCountValueToXml('.sm_total_hvd_c', result.hvd_app_con_ids.shift())
                    ids_hvd_con = result.hvd_app_con_ids
                    setCountValueToXml('.sm_total_my_hvd_sch_con', result.my_hvd_sch_con_ids.shift())
                    ids_hvd_sch_con = result.my_hvd_sch_con_ids
                    setCountValueToXml('.sm_total_phys', result.physiotherapy_app_sc_ids.shift())
                    ids_physiotherapy_sc = result.physiotherapy_app_sc_ids
                    setCountValueToXml('.sm_total_phys_hp', result.physiotherapy_app_co_ids.shift())
                    ids_physiotherapy_co = result.physiotherapy_app_co_ids
                    setCountValueToXml('.sm_total_phys_om', result.physiotherapy_app_op_ids.shift())
                    ids_physiotherapy_op = result.physiotherapy_app_op_ids
                    setCountValueToXml('.sm_total_phys_t', result.physiotherapy_app_tm_ids.shift())
                    ids_physiotherapy_tm = result.physiotherapy_app_tm_ids
                    setCountValueToXml('.sm_total_my_phy_all', result.my_phy_all_ids.shift())
                    ids_phy_all = result.my_phy_all_ids
                    setCountValueToXml('.sm_total_hhc', result.hhc_app_sch_ids.shift())
                    ids_hhc_sch = result.hhc_app_sch_ids
                    setCountValueToXml('.sm_total_hhc_c', result.hhc_app_hd_ids.shift())
                    ids_hhc_hd = result.hhc_app_hd_ids
                    setCountValueToXml('.sm_total_hhc_hn', result.hhc_app_hn_ids.shift())
                    ids_hhc_hn = result.hhc_app_hn_ids
                    setCountValueToXml('.sm_total_hhc_om', result.hhc_app_om_ids.shift())
                    ids_hhc_om = result.hhc_app_om_ids
                    setCountValueToXml('.sm_total_hhc_t', result.hhc_app_tm_ids.shift())
                    ids_hhc_tm = result.hhc_app_tm_ids
                    setCountValueToXml('.sm_total_my_hhc_all', result.my_hhc_sch_all_ids.shift())
                    ids_hhc_all = result.my_hhc_sch_all_ids
                    setCountValueToXml('.sm_total_my_tele_tod', result.my_tele_today_ids.shift())
                    ids_tele_today = result.my_tele_today_ids
                    setCountValueToXml('.sm_total_my_hvd_tod', result.my_hvd_today_ids.shift())
                    ids_hvd_today = result.my_hvd_today_ids
                    setCountValueToXml('.sm_total_my_hhc_tod', result.my_hhc_today_ids.shift())
                    ids_hhc_today = result.my_hhc_today_ids
                    setCountValueToXml('.sm_total_my_phy_tod', result.my_phy_today_ids.shift())
                    ids_phy_today = result.my_phy_today_ids
                    setCountValueToXml('.sm_total_my_pcr_tod', result.my_pcr_today_ids.shift())
                    ids_pcr_today = result.my_pcr_today_ids
                    setCountValueToXml('.sm_total_pcr_app', result.pcr_app_sch_ids.shift())
                    ids_pcr_sch = result.pcr_app_sch_ids
                    setCountValueToXml('.sm_total_pcr_opm', result.pcr_app_opm_ids.shift())
                    ids_pcr_opm = result.pcr_app_opm_ids
                    setCountValueToXml('.sm_total_pcr_app_team', result.pcr_app_tm_ids.shift())
                    ids_pcr_tm = result.pcr_app_tm_ids
                    setCountValueToXml('.sm_total_my_pcr_all', result.my_pcr_all_ids.shift())
                    ids_pcr_all = result.my_pcr_all_ids
                    setCountValueToXml('.oeh_total_service_request', result.service_request_ids.shift())
                    ids_ser_req = result.service_request_ids
                    setCountValueToXml('.oeh_total_notification', result.notification_ids.shift())
                    ids_not = result.notification_ids
                    setCountValueToXml('.sm_total_image_request', result.image_request_ids.shift())
                    ids_image_req = result.image_request_ids
                    setCountValueToXml('.sm_total_lab_request', result.lab_request_ids.shift())
                    ids_lab_rec = result.lab_request_ids
                    setCountValueToXml('.sm_total_investigation', result.investigation_ids.shift())
                    ids_inve = result.investigation_ids
                    setCountValueToXml('.oeh_total_referral', result.referral_ids.shift())
                    ids_ref = result.referral_ids
                    setCountValueToXml('.sm_total_payment', result.requested_payments_ids.shift())
                    ids_payments = result.requested_payments_ids
                    setCountValueToXml('.sm_total_send_payment', result.requested_payments_send_ids.shift())
                    ids_send_payments = result.requested_payments_send_ids
                    setCountValueToXml('.sm_total_paid_payment', result.requested_payments_paid_ids.shift())
                    ids_paid_payment = result.requested_payments_paid_ids
                    setCountValueToXml('.sm_total_cancellation_refund', result.cancellation_refund_ids.shift())
                    ids_cancellation = result.cancellation_refund_ids
                    setCountValueToXml('.sm_total_cancellation_refund_op', result.cancellation_refund_op_ids.shift())
                    ids_op_cancellation = result.cancellation_refund_op_ids
                    setCountValueToXml('.sm_total_cancellation_refund_pr', result.cancellation_refund_pr_ids.shift())
                    ids_pr_cancellation = result.cancellation_refund_pr_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_res_the', result.hhc_tod_tm_res_the_ids.shift())
                    ids_hhc_tod_tm_res_the = result.hhc_tod_tm_res_the_ids
                    setCountValueToXml('.sm_total_tele_tod_tm_res_the', result.tele_tod_tm_res_the_ids.shift())
                    ids_tele_tod_tm_res_the = result.tele_tod_tm_res_the_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_soc_wor', result.hhc_tod_tm_soc_wor_ids.shift())
                    ids_hhc_tod_tm_soc_wor = result.hhc_tod_tm_soc_wor_ids
                    setCountValueToXml('.sm_total_tele_tod_con_soc_wor', result.tele_tod_con_soc_wor_ids.shift())
                    ids_tele_tod_con_soc_wor = result.tele_tod_con_soc_wor_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_hhc_nurse', result.hhc_tod_tm_hhc_nurse_ids.shift())
                    ids_hhc_tod_tm_hhc_nurse = result.hhc_tod_tm_hhc_nurse_ids
                    setCountValueToXml('.sm_total_tele_tod_con_hhc_nurse', result.tele_tod_con_hhc_nurse_ids.shift())
                    ids_tele_tod_con_hhc_nurse = result.tele_tod_con_hhc_nurse_ids
                    setCountValueToXml('.sm_total_pcr_tod_tm_hhc_nurse', result.pcr_tod_tm_hhc_nurse_ids.shift())
                    ids_pcr_tod_team_hhc_nurse = result.pcr_tod_tm_hhc_nurse_ids
                    setCountValueToXml('.sm_total_pcr_tod_tm_lab_technician', result.pcr_tod_tm_lab_technician_ids.shift())
                    ids_pcr_tod_team_lab_technician = result.pcr_tod_tm_lab_technician_ids
                    setCountValueToXml('.sm_total_phy_tod_tm_hhc_phy', result.phy_tod_tm_hhc_phy_ids.shift())
                    ids_phy_tod_team_hhc_phy = result.phy_tod_tm_hhc_phy_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_hhc_phy', result.hhc_tod_tm_hhc_phy_ids.shift())
                    ids_hhc_tod_team_hhc_phy = result.hhc_tod_tm_hhc_phy_ids
                    setCountValueToXml('.sm_total_tele_tod_con_hhc_phy', result.tele_tod_con_hhc_phy_ids.shift())
                    ids_tele_tod_con_hhc_phy = result.tele_tod_con_hhc_phy_ids
                    setCountValueToXml('.sm_total_tele_tod_con_tele_app', result.tele_tod_con_tele_app_ids.shift())
                    ids_tele_tod_con_tele_app = result.tele_tod_con_tele_app_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_hhc_doctor', result.hhc_tod_tm_hhc_doctor_ids.shift())
                    ids_hhc_tod_team_hhc_doctor = result.hhc_tod_tm_hhc_doctor_ids
                    setCountValueToXml('.sm_total_tele_tod_con_hhc_doctor', result.tele_tod_con_hhc_doctor_ids.shift())
                    ids_tele_tod_con_hhc_doctor = result.tele_tod_con_hhc_doctor_ids
                    setCountValueToXml('.sm_total_hvd_tod_con_hhc_doctor', result.hvd_tod_con_hhc_doctor_ids.shift())
                    ids_hvd_tod_con_hhc_doctor = result.hvd_tod_con_hhc_doctor_ids
                    setCountValueToXml('.sm_total_tele_tod_con_head_phy', result.tele_tod_con_head_phy_ids.shift())
                    ids_tele_tod_con_head_phy = result.tele_tod_con_head_phy_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_head_phy', result.hhc_tod_tm_head_phy_ids.shift())
                    ids_hhc_tod_tm_head_phy = result.hhc_tod_tm_head_phy_ids
                    setCountValueToXml('.sm_total_phy_tod_tm_head_phy', result.phy_tod_tm_head_phy_ids.shift())
                    ids_phy_tod_tm_head_phy = result.phy_tod_tm_head_phy_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_head_nurse', result.hhc_tod_tm_head_nurse_ids.shift())
                    ids_hhc_tod_tm_head_nurse = result.hhc_tod_tm_head_nurse_ids
                    setCountValueToXml('.sm_total_pcr_tod_tm_head_nurse', result.pcr_tod_tm_head_nurse_ids.shift())
                    ids_pcr_tod_tm_head_nurse = result.pcr_tod_tm_head_nurse_ids
                    setCountValueToXml('.sm_total_hvd_tod_con_head_doctor', result.hvd_tod_con_head_doctor_ids.shift())
                    ids_hvd_tod_con_head_doctor = result.hvd_tod_con_head_doctor_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_head_doctor', result.hhc_tod_tm_head_doctor_ids.shift())
                    ids_hhc_tod_tm_head_doctor = result.hhc_tod_tm_head_doctor_ids
                    setCountValueToXml('.sm_total_call_center', result.call_center_ids.shift())
                    ids_call_center = result.call_center_ids
                    setCountValueToXml('.sm_total_call_center_op', result.call_center_op_ids.shift())
                    ids_call_center_op = result.call_center_op_ids
                    setCountValueToXml('.sm_total_hhc_vd', result.hhc_app_vd_ids.shift())
                    ids_hhc_vd = result.hhc_app_vd_ids
                    setCountValueToXml('.sm_total_hhc_inp', result.hhc_app_inp_ids.shift())
                    ids_hhc_inp = result.hhc_app_inp_ids
                    setCountValueToXml('.sm_total_hhc_ca', result.hhc_app_ca_ids.shift())
                    ids_hhc_ca = result.hhc_app_ca_ids
                    setCountValueToXml('.sm_total_web_req', result.web_req_ids.shift())
                    ids_web_req = result.web_req_ids
                    setCountValueToXml('.sm_total_phys_inp', result.physiotherapy_app_inp_ids.shift())
                    ids_physiotherapy_inp = result.physiotherapy_app_inp_ids
                    setCountValueToXml('.sm_total_phys_vd', result.physiotherapy_app_vd_ids.shift())
                    ids_physiotherapy_vd = result.physiotherapy_app_vd_ids
                    setCountValueToXml('.sm_total_phys_ca', result.physiotherapy_app_ca_ids.shift())
                    ids_physiotherapy_ca = result.physiotherapy_app_ca_ids





                    setCountValueToXml('.sm_total_my_hhc_t', result.my_hhc_app_tm_ids.shift())
                    ids_my_hhc_app_tem = result.my_hhc_app_tm_ids
                    setCountValueToXml('.sm_total_my_hhc_phy_tem', result.my_hhc_app_phy_tm_ids.shift())
                    ids_my_hhc_app_phys_tem = result.my_hhc_app_phy_tm_ids
                    setCountValueToXml('.sm_total_my_phys_t', result.my_physiotherapy_app_tm_ids.shift())
                    ids_my_physiotherapy_app_tem = result.my_physiotherapy_app_tm_ids
                    //                 console.log(result.my_physiotherapy_app_sch_ids)
                    setCountValueToXml('.sm_total_my_phys_sch', result.my_physiotherapy_app_sch_ids.shift())
                    ids_my_physiotherapy_app_sch = result.my_physiotherapy_app_sch_ids
                    setCountValueToXml('.sm_total_my_phys_hp', result.my_physiotherapy_app_hp_ids.shift())
                    ids_my_physiotherapy_app_hp = result.my_physiotherapy_app_hp_ids
                    setCountValueToXml('.sm_total_my_phys_op', result.my_physiotherapy_app_op_ids.shift())
                    ids_my_physiotherapy_app_op = result.my_physiotherapy_app_op_ids
                    setCountValueToXml('.sm_total_my_h_hhc_t', result.my_h_hhc_app_tm_ids.shift())
                    ids_my_h_hhc_app_tem = result.my_h_hhc_app_tm_ids
                    setCountValueToXml('.sm_total_my_tac', result.my_tele_app_con_ids.shift())
                    ids_my_tele_con = result.my_tele_app_con_ids
                    setCountValueToXml('.sm_total_my_hvd_c', result.my_hvd_app_con_ids.shift())
                    ids_my_hvd_con = result.my_hvd_app_con_ids
                    setCountValueToXml('.sm_total_my_hn_tac', result.my_tele_app_hn_con_ids.shift())
                    ids_my_hn_tele_con = result.my_tele_app_hn_con_ids
                    setCountValueToXml('.sm_total_my_hdphy_tac', result.my_tele_app_hdphy_con_ids.shift())
                    ids_my_hdphy_tele_con = result.my_tele_app_hdphy_con_ids
                    setCountValueToXml('.sm_total_my_hhcn_tac', result.my_tele_app_hhcn_con_ids.shift())
                    ids_my_hhcn_tele_con = result.my_tele_app_hhcn_con_ids
                    setCountValueToXml('.sm_total_my_hhcn_pcr', result.my_hhcn_pcr_app_tm_ids.shift())
                    ids_my_hhcn_pcr_con = result.my_hhcn_pcr_app_tm_ids
                    setCountValueToXml('.sm_total_my_hhphy_tele', result.my_tele_app_hhcphy_con_ids.shift())
                    ids_my_hhcphy_pcr_con = result.my_tele_app_hhcphy_con_ids
                    setCountValueToXml('.sm_total_my_rh_hhc_t', result.my_rh_hhc_app_tm_ids.shift())
                    ids_my_rh_hhc_app_tem = result.my_rh_hhc_app_tm_ids
                    setCountValueToXml('.sm_total_my_rh_tac', result.my_rh_tele_app_con_ids.shift())
                    ids_my_rh_tele_con = result.my_rh_tele_app_con_ids
                    setCountValueToXml('.sm_total_my_rh_hvd_c', result.my_rh_hvd_app_con_ids.shift())
                    ids_my_rh_hvd_con = result.my_rh_hvd_app_con_ids
                    // Sleep Medicine Request
                    setCountValueToXml('.sm_total_slep_me_req_unpaid', result.slep_me_req_unpaid_ids.shift())
                    ids_slep_me_req_unpaid = result.slep_me_req_unpaid_ids

                    setCountValueToXml('.sm_total_slep_me_req_paid', result.slep_me_req_paid_ids.shift())
                    ids_slep_me_req_paid = result.slep_me_req_paid_ids

                    setCountValueToXml('.sm_total_slep_me_req_ev', result.slep_me_req_ev_ids.shift())
                    ids_slep_me_req_ev = result.slep_me_req_ev_ids

                    setCountValueToXml('.sm_total_slep_me_req_sch', result.slep_me_req_sch_ids.shift())
                    ids_slep_me_req_sch = result.slep_me_req_sch_ids
                    // Caregiver Contract
                    setCountValueToXml('.sm_total_car_cont_unpaid', result.car_cont_unpaid_ids.shift())
                    ids_car_cont_unpaid = result.car_cont_unpaid_ids
                    setCountValueToXml('.sm_total_car_cont_paid', result.car_cont_paid_ids.shift())
                    ids_car_cont_paid = result.car_cont_paid_ids

                    setCountValueToXml('.sm_total_car_cont_ev', result.car_cont_ev_ids.shift())
                    ids_car_cont_ev = result.car_cont_ev_ids
                    setCountValueToXml('.sm_total_car_cont_as_car', result.car_cont_as_car_ids.shift())
                    ids_car_cont_as_car = result.car_cont_as_car_ids
                    setCountValueToXml('.sm_total_car_cont_act', result.car_cont_act_ids.shift())
                    ids_car_cont_act = result.car_cont_act_ids

                    setCountValueToXml('.sm_total_car_cont_rea_req', result.car_cont_rea_req_ids.shift())
                    ids_car_cont_rea_req = result.car_cont_rea_req_ids

                    setCountValueToXml('.sm_total_car_cont_hrq', result.car_cont_hrq_ids.shift())
                    ids_car_cont_hrq = result.car_cont_hrq_ids
                    setCountValueToXml('.sm_total_car_cont_trq', result.car_cont_trq_ids.shift())
                    ids_car_cont_trq = result.car_cont_trq_ids
                    setCountValueToXml('.sm_total_car_cont_rew', result.car_cont_rew_ids.shift())
                    ids_car_cont_rew = result.car_cont_rew_ids
                    setCountValueToXml('.sm_total_car_cont_hol', result.car_cont_hol_ids.shift())
                    ids_car_cont_hol = result.car_cont_hol_ids

                    setCountValueToXml('.sm_total_hhc_app_cr', result.hhc_app_cr_ids.shift())
                    ids_hhc_app_cr = result.hhc_app_cr_ids
                    setCountValueToXml('.sm_total_phy_app_cr', result.phy_app_cr_ids.shift())
                    ids_phy_app_cr = result.phy_app_cr_ids

                    setCountValueToXml('.sm_total_draft_payment', result.draft_payment_ids.shift())
                    ids_draft_payment = result.draft_payment_ids

                })
        },

        sm_filter_now: function (ev) {
            var self = this;
            /* Filter */
            $('.oeh_dashboard_filter_btn .btn').each(function (e) {
                this.classList.remove('btn-success')
            })
            ev.currentTarget.classList.add('btn-success')

            /* Dashboard Data */
            rpc.query({
                model: 'sm.dashboard',
                method: 'sm_data_now',
                args: [],
            })
                .then(function (result) {

                    setCountValueToXml('.sm_total_ta', result.tele_app_ids.shift())
                    ids_tele_sch = result.tele_app_ids
                    setCountValueToXml('.sm_missed_medicines', result.missed_medicines_ids.shift())
                    ids_missed_medicine = result.missed_medicines_ids
                    setCountValueToXml('.sm_cancel_medicines', result.cancel_medicines_ids.shift())
                    ids_cancel_medicine = result.cancel_medicines_ids
                    setCountValueToXml('.sm_total_tac', result.tele_app_con_ids.shift())
                    ids_tele_con = result.tele_app_con_ids
                    setCountValueToXml('.sm_total_my_tele_sch_con', result.my_tele_sch_con_ids.shift())
                    ids_tele_sch_con = result.my_tele_sch_con_ids
                    setCountValueToXml('.sm_total_hvd', result.hvd_app_sch_ids.shift())
                    ids_hvd_sch = result.hvd_app_sch_ids
                    setCountValueToXml('.sm_total_hvd_c', result.hvd_app_con_ids.shift())
                    ids_hvd_con = result.hvd_app_con_ids
                    setCountValueToXml('.sm_total_my_hvd_sch_con', result.my_hvd_sch_con_ids.shift())
                    ids_hvd_sch_con = result.my_hvd_sch_con_ids
                    setCountValueToXml('.sm_total_phys', result.physiotherapy_app_sc_ids.shift())
                    ids_physiotherapy_sc = result.physiotherapy_app_sc_ids
                    setCountValueToXml('.sm_total_phys_hp', result.physiotherapy_app_co_ids.shift())
                    ids_physiotherapy_co = result.physiotherapy_app_co_ids
                    setCountValueToXml('.sm_total_phys_om', result.physiotherapy_app_op_ids.shift())
                    ids_physiotherapy_op = result.physiotherapy_app_op_ids
                    setCountValueToXml('.sm_total_phys_t', result.physiotherapy_app_tm_ids.shift())
                    ids_physiotherapy_tm = result.physiotherapy_app_tm_ids
                    setCountValueToXml('.sm_total_my_phy_all', result.my_phy_all_ids.shift())
                    ids_phy_all = result.my_phy_all_ids
                    setCountValueToXml('.sm_total_hhc', result.hhc_app_sch_ids.shift())
                    ids_hhc_sch = result.hhc_app_sch_ids
                    setCountValueToXml('.sm_total_hhc_c', result.hhc_app_hd_ids.shift())
                    ids_hhc_hd = result.hhc_app_hd_ids
                    setCountValueToXml('.sm_total_hhc_hn', result.hhc_app_hn_ids.shift())
                    ids_hhc_hn = result.hhc_app_hn_ids
                    setCountValueToXml('.sm_total_hhc_om', result.hhc_app_om_ids.shift())
                    ids_hhc_om = result.hhc_app_om_ids
                    setCountValueToXml('.sm_total_hhc_t', result.hhc_app_tm_ids.shift())
                    ids_hhc_tm = result.hhc_app_tm_ids
                    setCountValueToXml('.sm_total_my_hhc_all', result.my_hhc_sch_all_ids.shift())
                    ids_hhc_all = result.my_hhc_sch_all_ids
                    setCountValueToXml('.sm_total_my_tele_tod', result.my_tele_today_ids.shift())
                    ids_tele_today = result.my_tele_today_ids
                    setCountValueToXml('.sm_total_my_hvd_tod', result.my_hvd_today_ids.shift())
                    ids_hvd_today = result.my_hvd_today_ids
                    setCountValueToXml('.sm_total_my_hhc_tod', result.my_hhc_today_ids.shift())
                    ids_hhc_today = result.my_hhc_today_ids
                    setCountValueToXml('.sm_total_my_phy_tod', result.my_phy_today_ids.shift())
                    ids_phy_today = result.my_phy_today_ids
                    setCountValueToXml('.sm_total_my_pcr_tod', result.my_pcr_today_ids.shift())
                    ids_pcr_today = result.my_pcr_today_ids
                    setCountValueToXml('.sm_total_pcr_app', result.pcr_app_sch_ids.shift())
                    ids_pcr_sch = result.pcr_app_sch_ids
                    setCountValueToXml('.sm_total_pcr_opm', result.pcr_app_opm_ids.shift())
                    ids_pcr_opm = result.pcr_app_opm_ids
                    setCountValueToXml('.sm_total_pcr_app_team', result.pcr_app_tm_ids.shift())
                    ids_pcr_tm = result.pcr_app_tm_ids
                    setCountValueToXml('.sm_total_my_pcr_all', result.my_pcr_all_ids.shift())
                    ids_pcr_all = result.my_pcr_all_ids
                    setCountValueToXml('.oeh_total_service_request', result.service_request_ids.shift())
                    ids_ser_req = result.service_request_ids
                    setCountValueToXml('.oeh_total_notification', result.notification_ids.shift())
                    ids_not = result.notification_ids
                    setCountValueToXml('.sm_total_image_request', result.image_request_ids.shift())
                    ids_image_req = result.image_request_ids
                    setCountValueToXml('.sm_total_lab_request', result.lab_request_ids.shift())
                    ids_lab_rec = result.lab_request_ids
                    setCountValueToXml('.sm_total_investigation', result.investigation_ids.shift())
                    ids_inve = result.investigation_ids
                    setCountValueToXml('.oeh_total_referral', result.referral_ids.shift())
                    ids_ref = result.referral_ids
                    setCountValueToXml('.sm_total_payment', result.requested_payments_ids.shift())
                    ids_payments = result.requested_payments_ids
                    setCountValueToXml('.sm_total_send_payment', result.requested_payments_send_ids.shift())
                    ids_send_payments = result.requested_payments_send_ids
                    setCountValueToXml('.sm_total_paid_payment', result.requested_payments_paid_ids.shift())
                    ids_paid_payment = result.requested_payments_paid_ids
                    setCountValueToXml('.sm_total_cancellation_refund', result.cancellation_refund_ids.shift())
                    ids_cancellation = result.cancellation_refund_ids
                    setCountValueToXml('.sm_total_cancellation_refund_op', result.cancellation_refund_op_ids.shift())
                    ids_op_cancellation = result.cancellation_refund_op_ids
                    setCountValueToXml('.sm_total_cancellation_refund_pr', result.cancellation_refund_pr_ids.shift())
                    ids_pr_cancellation = result.cancellation_refund_pr_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_res_the', result.hhc_tod_tm_res_the_ids.shift())
                    ids_hhc_tod_tm_res_the = result.hhc_tod_tm_res_the_ids
                    setCountValueToXml('.sm_total_tele_tod_tm_res_the', result.tele_tod_tm_res_the_ids.shift())
                    ids_tele_tod_tm_res_the = result.tele_tod_tm_res_the_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_soc_wor', result.hhc_tod_tm_soc_wor_ids.shift())
                    ids_hhc_tod_tm_soc_wor = result.hhc_tod_tm_soc_wor_ids
                    setCountValueToXml('.sm_total_tele_tod_con_soc_wor', result.tele_tod_con_soc_wor_ids.shift())
                    ids_tele_tod_con_soc_wor = result.tele_tod_con_soc_wor_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_hhc_nurse', result.hhc_tod_tm_hhc_nurse_ids.shift())
                    ids_hhc_tod_tm_hhc_nurse = result.hhc_tod_tm_hhc_nurse_ids
                    setCountValueToXml('.sm_total_tele_tod_con_hhc_nurse', result.tele_tod_con_hhc_nurse_ids.shift())
                    ids_tele_tod_con_hhc_nurse = result.tele_tod_con_hhc_nurse_ids
                    setCountValueToXml('.sm_total_pcr_tod_tm_hhc_nurse', result.pcr_tod_tm_hhc_nurse_ids.shift())
                    ids_pcr_tod_team_hhc_nurse = result.pcr_tod_tm_hhc_nurse_ids
                    setCountValueToXml('.sm_total_pcr_tod_tm_lab_technician', result.pcr_tod_tm_lab_technician_ids.shift())
                    ids_pcr_tod_team_lab_technician = result.pcr_tod_tm_lab_technician_ids
                    setCountValueToXml('.sm_total_phy_tod_tm_hhc_phy', result.phy_tod_tm_hhc_phy_ids.shift())
                    ids_phy_tod_team_hhc_phy = result.phy_tod_tm_hhc_phy_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_hhc_phy', result.hhc_tod_tm_hhc_phy_ids.shift())
                    ids_hhc_tod_team_hhc_phy = result.hhc_tod_tm_hhc_phy_ids
                    setCountValueToXml('.sm_total_tele_tod_con_hhc_phy', result.tele_tod_con_hhc_phy_ids.shift())
                    ids_tele_tod_con_hhc_phy = result.tele_tod_con_hhc_phy_ids
                    setCountValueToXml('.sm_total_tele_tod_con_tele_app', result.tele_tod_con_tele_app_ids.shift())
                    ids_tele_tod_con_tele_app = result.tele_tod_con_tele_app_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_hhc_doctor', result.hhc_tod_tm_hhc_doctor_ids.shift())
                    ids_hhc_tod_team_hhc_doctor = result.hhc_tod_tm_hhc_doctor_ids
                    setCountValueToXml('.sm_total_tele_tod_con_hhc_doctor', result.tele_tod_con_hhc_doctor_ids.shift())
                    ids_tele_tod_con_hhc_doctor = result.tele_tod_con_hhc_doctor_ids
                    setCountValueToXml('.sm_total_hvd_tod_con_hhc_doctor', result.hvd_tod_con_hhc_doctor_ids.shift())
                    ids_hvd_tod_con_hhc_doctor = result.hvd_tod_con_hhc_doctor_ids
                    setCountValueToXml('.sm_total_tele_tod_con_head_phy', result.tele_tod_con_head_phy_ids.shift())
                    ids_tele_tod_con_head_phy = result.tele_tod_con_head_phy_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_head_phy', result.hhc_tod_tm_head_phy_ids.shift())
                    ids_hhc_tod_tm_head_phy = result.hhc_tod_tm_head_phy_ids
                    setCountValueToXml('.sm_total_phy_tod_tm_head_phy', result.phy_tod_tm_head_phy_ids.shift())
                    ids_phy_tod_tm_head_phy = result.phy_tod_tm_head_phy_ids

                    setCountValueToXml('.sm_total_hhc_tod_tm_head_nurse', result.hhc_tod_tm_head_nurse_ids.shift())
                    ids_hhc_tod_tm_head_nurse = result.hhc_tod_tm_head_nurse_ids

                    setCountValueToXml('.sm_total_pcr_tod_tm_head_nurse', result.pcr_tod_tm_head_nurse_ids.shift())
                    ids_pcr_tod_tm_head_nurse = result.pcr_tod_tm_head_nurse_ids
                    setCountValueToXml('.sm_total_hvd_tod_con_head_doctor', result.hvd_tod_con_head_doctor_ids.shift())
                    ids_hvd_tod_con_head_doctor = result.hvd_tod_con_head_doctor_ids
                    setCountValueToXml('.sm_total_hhc_tod_tm_head_doctor', result.hhc_tod_tm_head_doctor_ids.shift())
                    ids_hhc_tod_tm_head_doctor = result.hhc_tod_tm_head_doctor_ids
                    setCountValueToXml('.sm_total_call_center', result.call_center_ids.shift())
                    ids_call_center = result.call_center_ids
                    setCountValueToXml('.sm_total_call_center_op', result.call_center_op_ids.shift())
                    ids_call_center_op = result.call_center_op_ids
                    setCountValueToXml('.sm_total_hhc_vd', result.hhc_app_vd_ids.shift())
                    ids_hhc_vd = result.hhc_app_vd_ids
                    setCountValueToXml('.sm_total_hhc_inp', result.hhc_app_inp_ids.shift())
                    ids_hhc_inp = result.hhc_app_inp_ids
                    setCountValueToXml('.sm_total_hhc_ca', result.hhc_app_ca_ids.shift())
                    ids_hhc_ca = result.hhc_app_ca_ids
                    setCountValueToXml('.sm_total_web_req', result.web_req_ids.shift())
                    ids_web_req = result.web_req_ids
                    setCountValueToXml('.sm_total_phys_inp', result.physiotherapy_app_inp_ids.shift())
                    ids_physiotherapy_inp = result.physiotherapy_app_inp_ids
                    setCountValueToXml('.sm_total_phys_vd', result.physiotherapy_app_vd_ids.shift())
                    ids_physiotherapy_vd = result.physiotherapy_app_vd_ids
                    setCountValueToXml('.sm_total_phys_ca', result.physiotherapy_app_ca_ids.shift())
                    ids_physiotherapy_ca = result.physiotherapy_app_ca_ids




                    setCountValueToXml('.sm_total_my_hhc_t', result.my_hhc_app_tm_ids.shift())
                    ids_my_hhc_app_tem = result.my_hhc_app_tm_ids
                    setCountValueToXml('.sm_total_my_hhc_phy_tem', result.my_hhc_app_phy_tm_ids.shift())
                    ids_my_hhc_app_phys_tem = result.my_hhc_app_phy_tm_ids
                    setCountValueToXml('.sm_total_my_phys_t', result.my_physiotherapy_app_tm_ids.shift())
                    ids_my_physiotherapy_app_tem = result.my_physiotherapy_app_tm_ids
                    //                 console.log(result.my_physiotherapy_app_sch_ids)
                    setCountValueToXml('.sm_total_my_phys_sch', result.my_physiotherapy_app_sch_ids.shift())
                    ids_my_physiotherapy_app_sch = result.my_physiotherapy_app_sch_ids
                    setCountValueToXml('.sm_total_my_phys_hp', result.my_physiotherapy_app_hp_ids.shift())
                    ids_my_physiotherapy_app_hp = result.my_physiotherapy_app_hp_ids
                    setCountValueToXml('.sm_total_my_phys_op', result.my_physiotherapy_app_op_ids.shift())
                    ids_my_physiotherapy_app_op = result.my_physiotherapy_app_op_ids
                    setCountValueToXml('.sm_total_my_h_hhc_t', result.my_h_hhc_app_tm_ids.shift())
                    ids_my_h_hhc_app_tem = result.my_h_hhc_app_tm_ids
                    setCountValueToXml('.sm_total_my_tac', result.my_tele_app_con_ids.shift())
                    ids_my_tele_con = result.my_tele_app_con_ids
                    setCountValueToXml('.sm_total_my_hvd_c', result.my_hvd_app_con_ids.shift())
                    ids_my_hvd_con = result.my_hvd_app_con_ids
                    setCountValueToXml('.sm_total_my_hn_tac', result.my_tele_app_hn_con_ids.shift())
                    ids_my_hn_tele_con = result.my_tele_app_hn_con_ids
                    setCountValueToXml('.sm_total_my_hdphy_tac', result.my_tele_app_hdphy_con_ids.shift())
                    ids_my_hdphy_tele_con = result.my_tele_app_hdphy_con_ids
                    setCountValueToXml('.sm_total_my_hhcn_tac', result.my_tele_app_hhcn_con_ids.shift())
                    ids_my_hhcn_tele_con = result.my_tele_app_hhcn_con_ids
                    setCountValueToXml('.sm_total_my_hhcn_pcr', result.my_hhcn_pcr_app_tm_ids.shift())
                    ids_my_hhcn_pcr_con = result.my_hhcn_pcr_app_tm_ids
                    setCountValueToXml('.sm_total_my_hhphy_tele', result.my_tele_app_hhcphy_con_ids.shift())
                    ids_my_hhcphy_pcr_con = result.my_tele_app_hhcphy_con_ids
                    setCountValueToXml('.sm_total_my_rh_hhc_t', result.my_rh_hhc_app_tm_ids.shift())
                    ids_my_rh_hhc_app_tem = result.my_rh_hhc_app_tm_ids
                    setCountValueToXml('.sm_total_my_rh_tac', result.my_rh_tele_app_con_ids.shift())
                    ids_my_rh_tele_con = result.my_rh_tele_app_con_ids
                    setCountValueToXml('.sm_total_my_rh_hvd_c', result.my_rh_hvd_app_con_ids.shift())
                    ids_my_rh_hvd_con = result.my_rh_hvd_app_con_ids
                    // Sleep Medicine Request
                    setCountValueToXml('.sm_total_slep_me_req_unpaid', result.slep_me_req_unpaid_ids.shift())
                    ids_slep_me_req_unpaid = result.slep_me_req_unpaid_ids

                    setCountValueToXml('.sm_total_slep_me_req_paid', result.slep_me_req_paid_ids.shift())
                    ids_slep_me_req_paid = result.slep_me_req_paid_ids

                    setCountValueToXml('.sm_total_slep_me_req_ev', result.slep_me_req_ev_ids.shift())
                    ids_slep_me_req_ev = result.slep_me_req_ev_ids

                    setCountValueToXml('.sm_total_slep_me_req_sch', result.slep_me_req_sch_ids.shift())
                    ids_slep_me_req_sch = result.slep_me_req_sch_ids
                    // Caregiver Contract
                    setCountValueToXml('.sm_total_car_cont_unpaid', result.car_cont_unpaid_ids.shift())
                    ids_car_cont_unpaid = result.car_cont_unpaid_ids
                    setCountValueToXml('.sm_total_car_cont_paid', result.car_cont_paid_ids.shift())
                    ids_car_cont_paid = result.car_cont_paid_ids

                    setCountValueToXml('.sm_total_car_cont_ev', result.car_cont_ev_ids.shift())
                    ids_car_cont_ev = result.car_cont_ev_ids
                    setCountValueToXml('.sm_total_car_cont_as_car', result.car_cont_as_car_ids.shift())
                    ids_car_cont_as_car = result.car_cont_as_car_ids
                    setCountValueToXml('.sm_total_car_cont_act', result.car_cont_act_ids.shift())
                    ids_car_cont_act = result.car_cont_act_ids

                    setCountValueToXml('.sm_total_car_cont_rea_req', result.car_cont_rea_req_ids.shift())
                    ids_car_cont_rea_req = result.car_cont_rea_req_ids

                    setCountValueToXml('.sm_total_car_cont_hrq', result.car_cont_hrq_ids.shift())
                    ids_car_cont_hrq = result.car_cont_hrq_ids
                    setCountValueToXml('.sm_total_car_cont_trq', result.car_cont_trq_ids.shift())
                    ids_car_cont_trq = result.car_cont_trq_ids
                    setCountValueToXml('.sm_total_car_cont_rew', result.car_cont_rew_ids.shift())
                    ids_car_cont_rew = result.car_cont_rew_ids
                    setCountValueToXml('.sm_total_car_cont_hol', result.car_cont_hol_ids.shift())
                    ids_car_cont_hol = result.car_cont_hol_ids

                    setCountValueToXml('.sm_total_hhc_app_cr', result.hhc_app_cr_ids.shift())
                    ids_hhc_app_cr = result.hhc_app_cr_ids
                    setCountValueToXml('.sm_total_phy_app_cr', result.phy_app_cr_ids.shift())
                    ids_phy_app_cr = result.phy_app_cr_ids

                    setCountValueToXml('.sm_total_draft_payment', result.draft_payment_ids.shift())
                    ids_draft_payment = result.draft_payment_ids

                })
        },

        renderElement: function (ev) {
            var self = this;
            $.when(this._super())
                .then(function (ev) {
                    $('#oeh_filter_btn_today').click()
                });
        },

        /* Load Telemedicine Appointment */
        load_telemedicine_appointment: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Telemedicine Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_tele_sch]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        /* Load Caregiver medicines state Missed*/
        load_caregive_missed_medicines: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Missed Medications"),
                type: 'ir.actions.act_window',
                res_model: 'sm.caregiver.medicine.schedule',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['id', 'in', ids_missed_medicine]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Caregiver medicines state Canceled */
        load_caregiver_canceled_medicines: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Canceled Mediciations"),
                type: 'ir.actions.act_window',
                res_model: 'sm.caregiver.medicine.schedule',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['id', 'in', ids_cancel_medicine]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        create_telemedicine_appointment: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Create Telemedicine Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.appointment',
                view_mode: 'form',
                views: [[false, 'form']],
                domain: [],
                target: 'new',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        create_hvd_appointment: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Create HVD Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hvd.appointment',
                view_mode: 'form',
                views: [[false, 'form']],
                domain: [],
                target: 'new',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        create_pt_appointment: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Create Physiotherapy Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.physiotherapy.appointment',
                view_mode: 'form',
                views: [[false, 'form']],
                domain: [],
                target: 'new',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        create_hhc_appointment: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Create HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'form',
                views: [[false, 'form']],
                domain: [],
                target: 'new',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        create_call_center: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Create Call Center Census"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.call.center.census',
                view_mode: 'form',
                views: [[false, 'form']],
                domain: [],
                target: 'new',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        /* Load Telemedicine Appointment Con */
        load_telemedicine_appointment_con: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Telemedicine Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_tele_con]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Tele Appointment Schedules + Confirmed  */
        load_tele_sch_con_appointment: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Telemedicine Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_tele_sch_con]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load HVD Appointment */
        load_hvd_appointment: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HVD Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hvd.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hvd_sch]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load HVD Appointment CO*/
        load_hvd_appointment_co: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HVD Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hvd.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hvd_con]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load HVD Appointment Schedules + Confirmed  */
        load_hvd_sch_con_appointment: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HVD Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hvd.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hvd_sch_con]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Physiotherapy Appointment */
        load_physiotherapy_appointment: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Physiotherapy Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.physiotherapy.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_physiotherapy_sc]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Physiotherapy Appointment HP */
        load_physiotherapy_appointment_hp: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Physiotherapy Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.physiotherapy.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_physiotherapy_co]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Physiotherapy Appointment OM */
        load_physiotherapy_appointment_om: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Physiotherapy Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.physiotherapy.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_physiotherapy_op]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Physiotherapy Appointment TE */
        load_physiotherapy_appointment_te: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Physiotherapy Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.physiotherapy.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_physiotherapy_tm]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Physiotherapy Appointment inprog */
        load_physiotherapy_appointment_inp: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Physiotherapy Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.physiotherapy.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_physiotherapy_inp]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Physiotherapy Appointment V.D. */
        load_physiotherapy_appointment_vd: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Physiotherapy Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.physiotherapy.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_physiotherapy_vd]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Physiotherapy Appointment cancel*/
        load_physiotherapy_appointment_ca: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Physiotherapy Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.physiotherapy.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_physiotherapy_ca]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        /* Load PHY Appointment Schedules + HP + OM + team  */
        load_phy_all_appointment: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Physiotherapist Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.physiotherapy.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_phy_all]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load HHC Appointment */
        load_hhc_appointment: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hhc_sch]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load HHC Appointment HD*/
        load_hhc_appointment_hd: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hhc_hd]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load call center */
        load_call_center: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Call Center Census"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.call.center.census',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_call_center]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load call center OP */
        load_call_center_op: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Call Center Census"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.call.center.census',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_call_center_op]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        /* Load HHC Appointment HN*/
        load_hhc_appointment_hn: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hhc_hn]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load HHC Appointment OM*/
        load_hhc_appointment_om: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hhc_om]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load HHC Appointment TE*/
        load_hhc_appointment_te: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hhc_tm]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load HHC Appointment VD*/
        load_hhc_appointment_vd: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hhc_vd]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load HHC Appointment InPrg*/
        load_hhc_appointment_inp: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hhc_inp]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load HHC Appointment cancel*/
        load_hhc_appointment_ca: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hhc_ca]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        load_web_req: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Service Web Request"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.web.request',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_web_req]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },


        /* Load HHC Appointment Schedules + HD + HN + OM + team  */
        load_hhc_all_appointment: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hhc_all]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load TELE Appointment Today Confirmed  */
        load_tele_appointment_today: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Telemedicine Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_tele_today]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load HVD Appointment Today Confirmed  */
        load_hvd_appointment_today: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HVD Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hvd.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hvd_today]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load HHC Appointment Today Team  */
        load_hhc_appointment_today: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hhc_today]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load PHY Appointment Today Team  */
        load_phy_appointment_today: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Physiotherapy Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.physiotherapy.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_phy_today]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load PCR Appointment Today Team  */
        load_pcr_appointment_today: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("PCR Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.pcr.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_pcr_today]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load PCR appointment */
        load_pcr_app: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("PCR Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.pcr.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_pcr_sch]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load PCR appointment operation_manager */
        load_pcr_app_opm: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("PCR Appointmrnt"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.pcr.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_pcr_opm]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load PCR appointment Team */
        load_pcr_app_t: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("PCR Appointmrnt"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.pcr.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_pcr_tm]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load PCR Appointment Schedules + OM + team  */
        load_pcr_all_appointment: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("PCR Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.pcr.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_pcr_all]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load CG./Sleep Med */
        load_sleep_med: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Service Request"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.service.request',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_ser_req]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load S.V. Consult */
        load_notification: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Notification"),
                type: 'ir.actions.act_window',
                res_model: 'sm.physician.notification',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_not]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Image Request */
        load_image_request: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Imaging Request"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.imaging.request',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_image_req]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Lab Request */
        load_lab_request: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Lab Request"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.lab.request',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_lab_rec]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Investigation */
        load_investigation_c: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Investigation"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.investigation',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_inve]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Referral */
        load_referral: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();

            this.do_action({
                name: _t("Referral"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.referral',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_ref]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Payment */
        load_payment: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Requested Payments"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.requested.payments',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_payments]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        // load send payment
        load_send_payment: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Requested Payments"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.requested.payments',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_send_payments]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load paid Payment */
        load_paid_payment: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Requested Payments"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.requested.payments',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_paid_payment]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Cancellation Refund */
        load_cancellation_refund: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Cancellation and Refund"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.cancellation.refund',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_cancellation]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Cancellation Op stateRefund */
        load_cancellation_op_refund: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Cancellation and Refund"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.cancellation.refund',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_op_cancellation]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Cancellation process state Refund */
        load_cancellation_pr_refund: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Cancellation and Refund"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.cancellation.refund',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_pr_cancellation]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load HHC Appointment Today Team IN Respiratory Therapist */
        load_hhc_app_tod_res_the: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hhc_tod_tm_res_the]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load tele Appointment Today Team IN Respiratory Therapist */
        load_tele_app_tod_res_the: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Telemedicine Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_tele_tod_tm_res_the]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load HHC Appointment Today Team IN Social Worker */
        load_hhc_app_tod_soc_wor: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hhc_tod_tm_soc_wor]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load tele Appointment Today Con IN Social Worker */
        load_tele_app_tod_soc_wor: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Telemedicine Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_tele_tod_con_soc_wor]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load HHC Appointment Today Team IN HHC Nurse */
        load_hhc_app_tod_hhc_nurse: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hhc_tod_tm_hhc_nurse]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load tele Appointment Today Team IN HHC Nurse */
        load_tele_app_tod_hhc_nurse: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Telemedicine Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_tele_tod_con_hhc_nurse]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load PCR Appointment Today Team IN HHC Nurse */
        load_pcr_app_tod_hhc_nurse: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("PCR Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.pcr.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_pcr_tod_team_hhc_nurse]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load PCR Appointment Today Team IN Lab Technician */
        load_pcr_app_tod_lab_technician: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("PCR Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.pcr.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_pcr_tod_team_lab_technician]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load PHY Appointment Today Team IN HHC PHY */
        load_phy_app_tod_hhc_phy: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Physiotherapy Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.physiotherapy.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_phy_tod_team_hhc_phy]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load HHC Appointment Today Team IN HHC PHY */
        load_hhc_app_tod_hhc_phy: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hhc_tod_team_hhc_phy]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Tele Appointment Today Con IN HHC PHY */
        load_tele_app_tod_hhc_phy: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Telemedicine Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_tele_tod_con_hhc_phy]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Tele Appointment Today Con IN Tele app */
        load_tele_app_tod_tele_app: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Telemedicine Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_tele_tod_con_tele_app]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load HHC Appointment Today Team IN HHC Doctor */
        load_hhc_app_tod_hhc_doctor: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hhc_tod_team_hhc_doctor]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Tele Appointment Today Con IN HHC Doctor */
        load_tele_app_tod_hhc_doctor: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Telemedicine Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_tele_tod_con_hhc_doctor]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load HVD Appointment Today Con IN HHC Doctor */
        load_hvd_app_tod_hhc_doctor: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HVD Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hvd.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hvd_tod_con_hhc_doctor]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Tele Appointment Today Con IN Head phy */
        load_tele_app_tod_head_phy: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Telemedicine Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_tele_tod_con_head_phy]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load HHC Appointment Today Team IN Head phy */
        load_hhc_app_tod_head_phy: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hhc_tod_tm_head_phy]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load PHY Appointment Today Team IN Head phy */
        load_phy_app_tod_head_phy: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Physiotherapy Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.physiotherapy.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_phy_tod_tm_head_phy]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load HHC Appointment Today Team IN Head Nurse */
        load_hhc_app_tod_head_nurse: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hhc_tod_tm_head_nurse]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load PCR Appointment Today Team IN Head Nurse */
        load_pcr_app_tod_head_nurse: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("PCR Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.pcr.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_pcr_tod_tm_head_nurse]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load HVD Appointment Today Con IN Head Doctor */
        load_hvd_app_tod_head_doctor: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HVD Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hvd.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hvd_tod_con_head_doctor]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load HHC Appointment Today Team IN Head Doctor */
        load_hhc_app_tod_head_doctor: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hhc_tod_tm_head_doctor]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },







        /* Load Lab Test */
        load_lab_test: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HVD Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hvd.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['state', '=', 'Confirmed']],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Patient */
        load_patient: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Patients"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.patient',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                // domain: [['user_id', '=', session.uid]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load MY Patient */
        load_my_patient: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Patients"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.patient',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                // domain: [['user_id', '=', session.uid]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Physician */
        load_physician: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Physician"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.physician',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                // domain: [['user_id', '=', session.uid]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Appointment */
        load_appointment: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                // domain: [['user_id', '=', session.uid]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load MY  Appointment */
        load_my_appointment: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Physician"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load MY HHC Appointment */
        load_my_hhc_appointment: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Physician"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                target: 'current',
                domain: [['state', '=', 'team']],
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Schedule */
        load_scheduled_apt: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Schedule"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Invoice */
        load_invoice: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Invoice"),
                type: 'ir.actions.act_window',
                res_model: 'account.move',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                // domain: [['user_id', '=', session.uid]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load Treatments */
        load_treatment: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Treatments"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.treatment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                // domain: [['user_id', '=', session.uid]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        /* Load MY Treatments */
        load_my_treatment: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("MY Treatments"),
                type: 'ir.actions.act_window',
                res_model: 'oeh.medical.treatment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                // domain: [['user_id', '=', session.uid]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },
        // Sleep Medicine Request
        load_unpaid_slep_me_req: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Sleep Medicine Request"),
                type: 'ir.actions.act_window',
                res_model: 'sm.sleep.medicine.request',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_slep_me_req_unpaid]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        load_paid_slep_me_req: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Sleep Medicine Request"),
                type: 'ir.actions.act_window',
                res_model: 'sm.sleep.medicine.request',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_slep_me_req_paid]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        load_ev_slep_me_req: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Sleep Medicine Request"),
                type: 'ir.actions.act_window',
                res_model: 'sm.sleep.medicine.request',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_slep_me_req_ev]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        load_sch_slep_me_req: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Sleep Medicine Request"),
                type: 'ir.actions.act_window',
                res_model: 'sm.sleep.medicine.request',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_slep_me_req_sch]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        // Caregiver Contract
        load_unpaid_car_cont: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Caregiver Contract"),
                type: 'ir.actions.act_window',
                res_model: 'sm.caregiver.contracts',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_car_cont_unpaid]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        load_paid_car_cont: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Caregiver Contract"),
                type: 'ir.actions.act_window',
                res_model: 'sm.caregiver.contracts',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_car_cont_paid]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        load_ev_car_cont: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Caregiver Contract"),
                type: 'ir.actions.act_window',
                res_model: 'sm.caregiver.contracts',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_car_cont_ev]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        load_car_cont_as_car: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Caregiver Contract"),
                type: 'ir.actions.act_window',
                res_model: 'sm.caregiver.contracts',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_car_cont_as_car]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        load_car_cont_act: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Caregiver Contract"),
                type: 'ir.actions.act_window',
                res_model: 'sm.caregiver.contracts',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_car_cont_act]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        load_car_cont_rea_req: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Caregiver Contract"),
                type: 'ir.actions.act_window',
                res_model: 'sm.caregiver.contracts',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_car_cont_rea_req]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        load_car_cont_hrq: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Caregiver Contract"),
                type: 'ir.actions.act_window',
                res_model: 'sm.caregiver.contracts',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_car_cont_hrq]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        load_car_cont_trq: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Caregiver Contract"),
                type: 'ir.actions.act_window',
                res_model: 'sm.caregiver.contracts',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_car_cont_trq]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        load_car_cont_rew: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Caregiver Contract"),
                type: 'ir.actions.act_window',
                res_model: 'sm.caregiver.contracts',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_car_cont_rew]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        load_car_cont_hol: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Caregiver Contract"),
                type: 'ir.actions.act_window',
                res_model: 'sm.caregiver.contracts',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_car_cont_hol]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        load_hhc_app_cr: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("HHC Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.hhc.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_hhc_app_cr]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        load_phy_app_cr: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Physiotherapy Appointment"),
                type: 'ir.actions.act_window',
                res_model: 'sm.shifa.physiotherapy.appointment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_phy_app_cr]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        load_draft_payment: function (e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            this.do_action({
                name: _t("Payment"),
                type: 'ir.actions.act_window',
                res_model: 'account.payment',
                view_mode: 'tree,form,kanban',
                views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
                domain: [['id', 'in', ids_draft_payment]],
                target: 'current',
            }, { reverse_breadcrumb: this.reverse_breadcrumb })
        },

        start: function () {
            var self = this;
            this.set("title", 'Sehati Dashboard');
            return this._super().then(function () {
                self.update_cp();
                self.render_dashboards();
                //                console.log(self)
            });
        },

        fetch_data: function () {
            var self = this;

            var def0 = self._rpc({
                model: 'oeh.dashboard',
                method: 'login_user_group'
            }).then(function (result) {
                self.group_no = result;
            });

            return $.when(def0);
        },

        render_dashboards: function () {
            var self = this;
            if (this.login_employee) {
                var templates = []
                //                console.log(self.group_no)
                switch (self.group_no) {
                    case 1:
                        templates = ['smDashboardFilter', 'HealthCenterAdmin'];
                        break;
                    case 2:
                        templates = ['smDashboardFilter', 'HealthCommandCenter'];
                        break;
                    case 3:
                        templates = ['smDashboardFilter', 'HealthCallCenter'];
                        break;
                    case 4:
                        templates = ['smDashboardFilter', 'HealthHeadDoctor'];
                        break;
                    case 5:
                        templates = ['smDashboardFilter', 'HealthHHCDoctor'];
                        break;
                    case 6:
                        templates = ['smDashboardFilter', 'HealthTelemedicineDoctor'];
                        break;
                    case 7:
                        templates = ['smDashboardFilter', 'HealthHeadNurse'];
                        break;
                    case 8:
                        templates = ['smDashboardFilter', 'HealthHeadPhysiotherapist'];
                        break;
                    case 9:
                        templates = ['smDashboardFilter', 'HealthHHCNurse'];
                        break;
                    case 10:
                        templates = ['smDashboardFilter', 'HealthHHCPhysiotherapist'];
                        break;
                    case 11:
                        templates = ['smDashboardFilter', 'HealthOperationsManager'];
                        break;
                    case 12:
                        templates = ['smDashboardFilter', 'HealthLabTechnician'];
                        break;
                    case 13:
                        templates = ['smDashboardFilter', 'HealthCaregiver'];
                        break;
                    case 14:
                        templates = ['smDashboardFilter', 'HealthSocialWorker'];
                        break;
                    case 15:
                        templates = ['smDashboardFilter', 'HealthRespiratoryTherapist'];
                        break;
                    case 16:
                        templates = ['smDashboardFilter', 'HealthClinicalDietitian'];
                        break;
                    case 17:
                        templates = ['smDashboardFilter', 'HealthHealthEducator'];
                        break;
                    case 18:
                        templates = ['smDashboardFilter', 'HealthDiabeticEducator'];
                        break;
                    case 19:
                        templates = ['smDashboardFilter', 'HealthHomeVisitDoctor'];
                        break;
                    case 20:
                        templates = ['smDashboardFilter', 'Accountant'];
                        break;
                    case 21:
                        templates = ['smDashboardFilter', 'SupervisorCaregiver'];
                        break;

                }

                _.each(templates, function (template) {
                    self.$('.oeh_main_dashboard').append(QWeb.render(template, { widget: self }));
                });
            }
            else {
                self.$('.oeh_main_dashboard').append(QWeb.render('EmployeeWarning', { widget: self }));
            }
        },

        reverse_breadcrumb: function () {
            var self = this;
            web_client.do_push_state({});
            // this.update_cp();
            this.fetch_data().then(function () {
                self.$('.oeh_main_dashboard').reload();
                self.render_dashboards();
            });
        },

        update_cp: function () {
            var self = this;
        },
    });

    core.action_registry.add('smartmind_dashboard', OehDashBoard);
    return OehDashBoard;
});