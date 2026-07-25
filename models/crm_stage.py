# -*- coding: utf-8 -*-
from odoo import models, fields

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
