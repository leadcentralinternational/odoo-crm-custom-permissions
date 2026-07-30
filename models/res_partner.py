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
        # Do not restrict superuser/admin or users without custom permissions
        if not self.env.su and user.crm_custom_permissions_enabled and not user.has_group('base.group_system'):
            if not self.env.context.get('skip_custom_crm_filter'):
                allowed_partner_ids = list(filter(None, [user.partner_id.id, user.company_id.partner_id.id]))
                prospect_domain = [
                    '|', ('x_is_lead_prospect', '=', True),
                    '|', ('id', 'in', allowed_partner_ids),
                    ('user_ids', '!=', False)
                ]
                domain = expression.AND([domain, prospect_domain])
        return super()._search(domain, offset=offset, limit=limit, order=order, **kwargs)
