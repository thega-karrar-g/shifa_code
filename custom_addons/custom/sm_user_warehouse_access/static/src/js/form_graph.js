odoo.define('sm_vital_signs.FormGraph', function (require) {
    'use strict';

    var FormRenderer = require('web.FormRenderer');
    var BasicRenderer = require('web.BasicRenderer');
    var rpc = require('web.rpc');
    var FormController = require('web.FormController');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var dialogs = require('web.view_dialogs');

    var _t = core._t;
    var qweb = core.qweb;

    var get_line_colors = function(data, limits) {
        var colorArr = [];
        for (let j=0; j<data.length; ++j) {
            if (parseFloat(data[j])< parseFloat(limits[0]) | parseFloat(data[j]) > parseFloat(limits[1])) {
                colorArr.push("red");
            } else {
                colorArr.push("green");
            }
        }
        return colorArr;
    };

    FormRenderer.include({
        _renderView: function () {
            var self = this;

            // render the form and evaluate the modifiers
            var defs = [];
            this.defs = defs;
            this.inactiveNotebooks = [];
            var $form = this._renderNode(this.arch).addClass(this.className);
            delete this.defs;
//            var recordId = $(Object)[0].ATTRIBUTE_NODE;
            if (this.state && this.state.res_id) {
              var recordId = this.state.res_id;
              // Rest of your code that uses the recordId variable
            } else {
              // Handle the case when this.state.res_id is undefined or null
            }
            return rpc.query({
                model: 'sm.patient',
                method: 'get_charts_data',
                args: [recordId],
            })
            .then(function (result) {

                for (let i=0; i<result.length; ++i) {
                    var canvas_id = '#'+ result[i]['canvas_id'];
                    var ctx = $form.find(canvas_id);
                    console.log(ctx);
                    var labels = result[i]['labels'];
                    var label = result[i]['label'];
                    var datas = result[i]['datas'];
                    var limits = result[i]['limits'];
                    var dataSets =[];

                    datas.forEach((data, indx) => {
                        var colorArr = get_line_colors(data, limits[indx]);
                        dataSets.push({
                            data: data,
                            label: label,
                            pointBackgroundColor: colorArr,
                            pointBorderColor: colorArr,
                            fillColor:colorArr,
                        });
                    });

                    var chart = new Chart(ctx, {
                        type: "line",
                        data: {
                            labels: labels,
                            datasets: dataSets,
                            },
                            options: {}
                    });

                    console.log(chart);
                }

                return Promise.all(defs).then(() => self.__renderView()).then(function () {
                    self._updateView($form.contents());
                    if (self.state.res_id in self.alertFields) {
                        self.displayTranslationAlert();
                    }
                }).then(function(){
                    if (self.lastActivatedFieldIndex >= 0) {
                        self._activateNextFieldWidget(self.state, self.lastActivatedFieldIndex);
                    }

                }).guardedCatch(function () {
                    $form.remove();
                });

            });
        },

    });
});

