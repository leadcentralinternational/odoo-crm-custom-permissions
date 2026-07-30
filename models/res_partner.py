# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.osv import expression

class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_is_lead_prospect = fields.Boolean(
        string="Es Prospecto (Cliente-Lead)",
        default=False,
        help="Indica si este contacto es un prospecto de lead y no un cliente comprador."
    )

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, **kwargs):
        user = self.env.user
        if user.crm_custom_permissions_enabled and not user.has_group('base.group_system'):
            # Restricted users can only see contacts marked as lead prospects
            prospect_domain = [('x_is_lead_prospect', '=', True)]
            domain = expression.AND([domain, prospect_domain])
        return super()._search(domain, offset=offset, limit=limit, order=order, **kwargs)
