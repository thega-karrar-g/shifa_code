odoo.define('web.web_widget_image_annotation', function(require) {
    "use strict";

    var field_registry = require('web.field_registry');
    var fields = require('web.basic_fields');
    var FormController = require('web.FormController');

    var FieldImageAnnotation = fields.FieldBinaryImage.extend({

        template: 'ImageAnnotation',

        init: function() {
            var self = this;
            this._super.apply(this, arguments);
        },
        start: function() {
            this._super.apply(this, arguments);
            var self = this;
            if (this.mode === "readonly") {

            }else{
            var field_desc = 'R0lGODlhAQABAIAAAAUEBAAAACwAAAAAAQABAAACAkQBADs'
                var field_name = this.nodeOptions.preview_image ?
                    this.nodeOptions.preview_image :
                    this.name;
                    self._rpc({
                        model: this.model,
                        method: 'read',
                        args: [this.res_id, [field_name]]
                    }).then(function(data) {
                        if (data) {
                                var field_des = _.values(_.pick(data[0], field_name))[0];
                            if(field_des){
                            field_desc = field_des
                                self.$el.imageMaker({
                                    templates:[
                                        {url: 'data:image/png;base64,'+field_desc, title:'Image'},
                                    ],
                                    downloadGeneratedImage:false,
                                    onGenerate:function(data, formData) {
                                    var img_data_base64 = data.amm_canvas.split(',')[1];
                                    var approx_img_size = 3 * (img_data_base64.length / 4)

                                    self.on_file_uploaded(approx_img_size, "web-cam-preview.jpeg", "image/jpeg", img_data_base64);
                                    }
                                })
                             }
                             else{
                                self.$el.imageMaker({
                                    templates:[
                                        {url: 'data:image/png;base64,'+field_desc, title:'Image'},
                                    ],
                                    downloadGeneratedImage:false,
                                    onGenerate:function(data, formData) {
                                    var img_data_base64 = data.amm_canvas.split(',')[1];
                                    var approx_img_size = 3 * (img_data_base64.length / 4)

                                    self.on_file_uploaded(approx_img_size, "web-cam-preview.jpeg", "image/jpeg", img_data_base64);
                                    }
                                })
                        }
                        }

                    });

            }

        },

        _renderEdit: function () {
            this.$('> img').remove();
        },
    });

        field_registry
        .add('imageannotation', FieldImageAnnotation);

return {
    FieldImageAnnotation: FieldImageAnnotation
};

});
