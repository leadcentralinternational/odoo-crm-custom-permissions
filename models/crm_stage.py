# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class CrmStage(models.Model):
    _inherit = 'crm.stage'

    send_email_on_entry = fields.Boolean(
        string='Send Email to Client',
        default=False,
        help='If checked, an email will be automatically sent to the customer when a lead enters this stage.'
    )
    email_template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        domain="[('model', '=', 'crm.lead')]",
        help='The email template to send to the customer.'
    )

    @api.model_create_multi
    def create(self, vals_list):
        user = self.env.user
        if user.crm_custom_permissions_enabled and not user.has_group('base.group_system'):
            if not user.crm_can_create_stages:
                raise UserError(_("Permission denied. You are not allowed to create CRM stages."))
        return super().create(vals_list)

