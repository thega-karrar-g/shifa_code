odoo.define('bt_document_share_public.AttachmentLink', function (require) {
"use strict";

var core = require('web.core');
var Chatter = require('mail.Chatter');
var Widget = require('web.Widget');

var AttachmentLink =  Chatter.include({
		
	init: function () {
        	this._super.apply(this, arguments); 
		this.events = _.extend(this.events, {
        		"click .o_chatter_button_attachment_link": '_onClickAttachmentLinkButton',
        	});       	        	
    	},	
	
    	    		
   	_onClickAttachmentLinkButton: function () {	
			
            var self = this;
	    var context = {};

            if (self.context.default_model && self.context.default_res_id) {
        	context.active_model = self.context.default_model;
            	context.default_res_id = self.context.default_res_id;
            	context.active_id = self.context.default_res_id;
            }
            var action = {
                type: 'ir.actions.act_window',
                name: "Attachments",
                res_model: 'attachment.link',		                
                target: 'new',
                views: [[false, 'form']], 
                type : 'form',
                view_mode : 'form',
		        context: context,
            };
            self.do_action(action);
        },		    	
});

return AttachmentLink;
});
