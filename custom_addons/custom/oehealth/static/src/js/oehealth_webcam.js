/*
    Copyright (C) 2019 oeHealth (<http://oehealth.in>). All Rights Reserved
    oeHealth, Hospital Management Solutions

 Odoo Proprietary License v1.0

 This software and associated files (the "Software") may only be used (executed,
 modified, executed after modifications) if you have purchased a valid license
 from the authors, typically via Odoo Apps, oeHealth.in, braincrewapps.com, or if you have received a written
 agreement from the authors of the Software.

 You may develop Odoo modules that use the Software as a library (typically
 by depending on it, importing it and using its resources), but without copying
 any source code or material from the Software. You may distribute those
 modules under the license of your choice, provided that this license is
 compatible with the terms of the Odoo Proprietary License (For example:
 LGPL, MIT, or proprietary licenses similar to this one).

 It is forbidden to publish, distribute, sublicense, or sell copies of the Software
 or modified copies of the Software.

 The above copyright notice and this permission notice must be included in all
 copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
 DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
 ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 DEALINGS IN THE SOFTWARE.

*/

odoo.define('oehealth.webcam_widget', function(require) {
    "use strict";

    var core = require('web.core');
    var FieldBinaryImage = require('web.basic_fields').FieldBinaryImage;
    var rpc = require('web.rpc')
    var Dialog = require('web.Dialog');

    var _t = core._t;
    var QWeb = core.qweb;

    FieldBinaryImage.include({

        _render: function () {
            this._super();
            var html_el;
            var self = this,
                WebCamDialog = $(QWeb.render("WebCamDialog")),
                img_data;

            html_el = $(WebCamDialog).find('#live_webcam');
            Webcam.set({
                width: 320,
                height: 240,
                image_format: 'jpeg',
                jpeg_quality: 90,
                swfURL: '/static/src/js/webcam.swf',
            });

            self.$el.find('.o_form_binary_file_web_cam').removeClass('col-md-offset-5');

            self.$el.find('.o_form_binary_file_web_cam').off().on('click', function(){
                // Init Webcam
                new Dialog(self, {
                    size: 'large',
                    dialogClass: 'o_act_window',
                    title: _t("Patient Picture"),
                    $content: WebCamDialog,
                    buttons: [
                        {
                            text: _t("Take Snap"), classes: 'btn-primary take_snap_btn',
                            click: function () {
                                Webcam.snap( function(data) {
                                    img_data = data;
                                    // Display Snap besides Live WebCam Preview
                                    WebCamDialog.find("#webcam_result").html('<img src="'+img_data+'"/>');
                                });
                                $('.save_close_btn').removeAttr('disabled');
                            }
                        },
                        {
                            text: _t("Save & Close"), classes: 'btn-primary save_close_btn', close: true,
                            click: function () {
                                var img_data_base64 = img_data.split(',')[1];
                                var approx_img_size = 3 * (img_data_base64.length / 4)

                                self.on_file_uploaded(approx_img_size, "web-cam-preview.jpeg", "image/jpeg", img_data_base64);
                            }
                        },
                        {
                            text: _t("Close"), close: true
                        }
                    ]
                }).open();
                Webcam.attach(html_el[0]);
                $('.save_close_btn').attr('disabled', 'disabled');
                WebCamDialog.find("#webcam_result").html('<img src="/oehealth/static/src/img/placeholder.png"/>');
            });
        },
    });

    Dialog.include({
        destroy: function () {
            Webcam.reset();
            this._super.apply(this, arguments);
        },
    });

});
