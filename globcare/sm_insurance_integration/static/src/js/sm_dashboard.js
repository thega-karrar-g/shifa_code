odoo.define("sm_insurance_integration.SMInsDashboard", function (require) {
  "use strict";
  //const ActionMenus = require('web.ActionMenus');

  var AbstractAction = require("web.AbstractAction");
  var ajax = require("web.ajax");
  var core = require("web.core");
  var rpc = require("web.rpc");
  var web_client = require("web.web_client");
  var session = require("web.session");
  var _t = core._t;
  var QWeb = core.qweb;
  var self = this;
    // dashboard vars

  // dashboard vars
  var  ids_eligibility_request_sent,ids_eligibility_request_processed,ids_authorization_request_sent,ids_authorization_request_processed
     = new Array();

  var img,
    name = "";

  function setCountValueToXml(className, count) {
    $(className).empty();
    $(className).append("<h1><b>" + count + "</b></h1>");
  }

  function setNameValueToXml(className, name) {
    $(className).empty();
    $(className).append(
      '<p style=" margin-top: 13px; font-size: large; color: #637e97; "> Hello, ' +
        name +
        "</h1>"
    );
  }

  function setSrcValueToXml(className, url) {
    $(className).empty();
    $(className).append(
      '<img src="' +
        url +
        '"style=" width: 100px; height: 100px; padding: 1px; border: 2px solid #36c0e1;  border-radius: 50%;"/>'
    );
  }

  var HisDashBoard = AbstractAction.extend({
    contentTemplate: "SMInsDashboard",

    events: {

      "click .load_eligibility_request_sent": "load_eligibility_request_sent",
      "click .load_eligibility_request_processed": "load_eligibility_request_processed",
      "click .load_authorization_request_sent": "load_authorization_request_sent",
      "click .load_authorization_request_processed": "load_authorization_request_processed",


      "click #home_filter_btn_today": "sm_filter_today",
      "click #home_filter_btn_week": "sm_filter_week",
      "click #home_filter_btn_month": "sm_filter_month",
      "click #home_filter_btn_now": "sm_filter_now",
    },

    init: function (parent, context) {
      this._super(parent, context);
      this.dashboards_templates = [
        "SMInsDashboardFilter",
        "Admin",
      ];
      this.login_employee = [];
    },

    willStart: function () {
      var self = this;
      this.login_employee = {};
      $("#home_curr_day_patient").addClass("d-none");
      $("#home_curr_week_patient").addClass("d-none");
      $("#home_curr_month_patient").addClass("d-none");
      $("#home_total_patient").addClass("d-none");
      return Promise.all([
        this._super.apply(this, arguments),
        this.prefill()
      ]);
    },

    prefill: function () {
      var self = this
      self._rpc({
        model: "sm.insurance.dashboard",
        method: "login_user_img_url",
      })
      .then(function (result) {
        self.img = result.img_url;
        self.name = result.name;
      });
    var def0 = self
      ._rpc({
        model: "sm.insurance.dashboard",
        method: "login_user_group",
      })
      .then(function (result) {
        self.group_no = result;
      });
    return $.when(def0);
    },

    sm_filter_today: function (ev) {
      ev.preventDefault();
      var self = this;
      /* Filter */
      $(".sm_dashboard_filter_btn .btn").each(function (e) {
        this.classList.remove("btn-success");
      });
      ev.currentTarget.classList.add("btn-success");

      /* Dashboard Data */
      rpc
        .query({
          model: "sm.insurance.dashboard",
          method: "sm_data_today",
          args: [],
        })
        .then(function (result) {
          // referral
          setCountValueToXml(
            ".sm_total_eligibility_request_sent",
            result.eligibility_request_sent_ids.shift()
          );
          ids_eligibility_request_sent = result.eligibility_request_sent_ids

          setCountValueToXml(
            ".sm_total_eligibility_request_processed",
            result.eligibility_request_processed_ids.shift()
          );
          ids_eligibility_request_processed = result.eligibility_request_processed_ids

          setCountValueToXml(
            ".sm_total_authorization_request_sent",
            result.authorization_request_sent_ids.shift()
          );
          ids_authorization_request_sent = result.authorization_request_sent_ids

          setCountValueToXml(
            ".sm_total_authorization_request_processed",
            result.authorization_request_processed_ids.shift()
          );
          ids_authorization_request_processed = result.authorization_request_processed_ids




          setNameValueToXml(".user_name", self.name);
          setSrcValueToXml(".img_url", self.img);
        });
    },

    sm_filter_week: function (ev) {
      ev.preventDefault();
      var self = this;
      /* Filter */
      $(".sm_dashboard_filter_btn .btn").each(function (e) {
        this.classList.remove("btn-success");
      });
      ev.currentTarget.classList.add("btn-success");

      /* Dashboard Data */
      rpc
        .query({
          model: "sm.insurance.dashboard",
          method: "sm_data_week",
          args: [],
        })
        .then(function (result) {
          console.log(result);

          // referral
          setCountValueToXml(
            ".sm_total_eligibility_request_sent",
            result.eligibility_request_sent_ids.shift()
          );
          ids_eligibility_request_sent = result.eligibility_request_sent_ids

          setCountValueToXml(
            ".sm_total_eligibility_request_processed",
            result.eligibility_request_processed_ids.shift()
          );
          ids_eligibility_request_processed = result.eligibility_request_processed_ids

          setCountValueToXml(
            ".sm_total_authorization_request_sent",
            result.authorization_request_sent_ids.shift()
          );
          ids_authorization_request_sent = result.authorization_request_sent_ids

          setCountValueToXml(
            ".sm_total_authorization_request_processed",
            result.authorization_request_processed_ids.shift()
          );
          ids_authorization_request_processed = result.authorization_request_processed_ids

          setNameValueToXml(".user_name", self.name);
          setSrcValueToXml(".img_url", self.img);
        });
    },

    sm_filter_month: function (ev) {
      ev.preventDefault();
      var self = this;
      /* Filter */
      $(".sm_dashboard_filter_btn .btn").each(function (e) {
        this.classList.remove("btn-success");
      });
      ev.currentTarget.classList.add("btn-success");

      /* Dashboard Data */
      rpc
        .query({
          model: "sm.insurance.dashboard",
          method: "sm_data_month",
          args: [],
        })
        .then(function (result) {

          setCountValueToXml(
            ".sm_total_eligibility_request_sent",
            result.eligibility_request_sent_ids.shift()
          );
          ids_eligibility_request_sent = result.eligibility_request_sent_ids

          setCountValueToXml(
            ".sm_total_eligibility_request_processed",
            result.eligibility_request_processed_ids.shift()
          );
          ids_eligibility_request_processed = result.eligibility_request_processed_ids

          setCountValueToXml(
            ".sm_total_authorization_request_sent",
            result.authorization_request_sent_ids.shift()
          );
          ids_authorization_request_sent = result.authorization_request_sent_ids

          setCountValueToXml(
            ".sm_total_authorization_request_processed",
            result.authorization_request_processed_ids.shift()
          );
          ids_authorization_request_processed = result.authorization_request_processed_ids



          setNameValueToXml(".user_name", self.name);
          setSrcValueToXml(".img_url", self.img);
        });
    },

    sm_filter_now: function (ev) {
      ev.preventDefault();
      var self = this;
      /* Filter */
      $(".sm_dashboard_filter_btn .btn").each(function (e) {
        this.classList.remove("btn-success");
      });
      ev.currentTarget.classList.add("btn-success");

      /* Dashboard Data */
      rpc
        .query({
          model: "sm.insurance.dashboard",
          method: "sm_data_now",
          args: [],
        })
        .then(function (result) {

          setCountValueToXml(
            ".sm_total_eligibility_request_sent",
            result.eligibility_request_sent_ids.shift()
          );
          ids_eligibility_request_sent = result.eligibility_request_sent_ids

          setCountValueToXml(
            ".sm_total_eligibility_request_processed",
            result.eligibility_request_processed_ids.shift()
          );
          ids_eligibility_request_processed = result.eligibility_request_processed_ids

          setCountValueToXml(
            ".sm_total_authorization_request_sent",
            result.authorization_request_sent_ids.shift()
          );
          ids_authorization_request_sent = result.authorization_request_sent_ids

          setCountValueToXml(
            ".sm_total_authorization_request_processed",
            result.authorization_request_processed_ids.shift()
          );
          ids_authorization_request_processed = result.authorization_request_processed_ids



          setNameValueToXml(".user_name", self.name);
          setSrcValueToXml(".img_url", self.img);
        });
    },






    load_eligibility_request_sent: function (e) {
      var self = this;
      e.stopPropagation();
      e.preventDefault();
      this.do_action(
        {
          name: _t("Eligibility Request(sent)"),
          type: "ir.actions.act_window",
          res_model: "sm.eligibility.check.request",
          view_mode: "tree,form,kanban",
          views: [
            [false, "list"],
            [false, "form"],
            [false, "kanban"],
          ],
          domain: [["id", "in", ids_eligibility_request_sent]],
          target: "current",
        },
        { reverse_breadcrumb: this.reverse_breadcrumb }
      );
    },

    load_eligibility_request_processed: function (e) {
      var self = this;
      e.stopPropagation();
      e.preventDefault();
      this.do_action(
        {
          name: _t("eligibility_request(sent)"),
          type: "ir.actions.act_window",
          res_model: "sm.eligibility.check.request",
          view_mode: "tree,form,kanban",
          views: [
            [false, "list"],
            [false, "form"],
            [false, "kanban"],
          ],
          domain: [["id", "in", ids_eligibility_request_processed]],
          target: "current",
        },
        { reverse_breadcrumb: this.reverse_breadcrumb }
      );
    },

    load_authorization_request_sent: function (e) {
      var self = this;
      e.stopPropagation();
      e.preventDefault();
      this.do_action(
        {
          name: _t("authorization request(sent)"),
          type: "ir.actions.act_window",
          res_model: "sm.pre.authorization.request",
          view_mode: "tree,form,kanban",
          views: [
            [false, "list"],
            [false, "form"],
            [false, "kanban"],
          ],
          domain: [["id", "in", ids_authorization_request_sent]],
          target: "current",
        },
        { reverse_breadcrumb: this.reverse_breadcrumb }
      );
    },

    load_authorization_request_processed: function (e) {
      var self = this;
      e.stopPropagation();
      e.preventDefault();
      this.do_action(
        {
          name: _t("authorization request(processed)"),
          type: "ir.actions.act_window",
          res_model: "sm.pre.authorization.request",
          view_mode: "tree,form,kanban",
          views: [
            [false, "list"],
            [false, "form"],
            [false, "kanban"],
          ],
          domain: [["id", "in", ids_authorization_request_processed]],
          target: "current",
        },
        { reverse_breadcrumb: this.reverse_breadcrumb }
      );
    },



    start: async function () {
      var def = this._super.apply(this, arguments);
      this.set("title", "SM Dashboard");
      var self = this;
      self.update_cp();
      self.render_dashboards();
      await self.$("#home_filter_btn_today").trigger("click");
      return def;
    },

    fetch_data: function () {
      var self = this;
      var def0 = self
        ._rpc({
          model: "sm.insurance.dashboard",
          method: "login_user_group",
        })
        .then(function (result) {
          self.group_no = result;
        });

      return $.when(def0);
    },

    render_dashboards: function () {
      var self = this;
      if (this.login_employee) {
        var templates = [];
        switch (self.group_no) {
          case 1:
            templates = ["SMInsDashboardFilter", "ReayhAdminInsu"];
            break;
          case 2:
            templates = ["SMInsDashboardFilter", "AdminInsu"];
            break;
          case 3:
            templates = ["SMInsDashboardFilter", "OperationMangerInsu"];
            break;
          case 4:
            templates = ["SMInsDashboardFilter", "physicianInsu"];
            break;



        }

        _.each(templates, function (sm_dashboard_referral_template) {
          self
            .$(".home_main_refdashboard")
            .append(QWeb.render(sm_dashboard_referral_template, { widget: self }));
        });
      } else {
        self
          .$(".home_main_refdashboard")
          .append(QWeb.render("EmployeeWarning", { widget: self }));
      }
    },

    reverse_breadcrumb: function () {
      var self = this;
      web_client.do_push_state({});
      this.update_cp();
      this.fetch_data().then(function () {
        //self.$(".home_main_refdashboard").reload();
        self.render_dashboards();
      });
    },

    update_cp: function () {
      var self = this;
    },
  });

  core.action_registry.add("sm_insurance_integration", HisDashBoard);
  return HisDashBoard;
});

function addClassById(elementId, className) {
  var element = document.getElementById(elementId);
  if (element) {
    element.classList.add(className);
  }
}

// Remove a class from an element
function removeClassById(elementId, className) {
  var element = document.getElementById(elementId);
  if (element) {
    element.classList.remove(className);
  }
}

function setShakeIcon(itemIdVal, iconIdVal) {
  try {
    const waiting_id_val = document.getElementById(itemIdVal).innerText;
    if (waiting_id_val == 0) {
      removeClassById(iconIdVal, "animate-spin"); // waiting-for-action
    } else {
      addClassById(iconIdVal, "animate-spin");
    }
  } catch (error) {
    // Code to handle the error
  }
}