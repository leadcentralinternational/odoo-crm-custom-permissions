# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.osv import expression

class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_is_lead_prospect = fields.Boolean(
        string="Is Prospect (Lead-Client)",
        default=False,
        help="Indicates whether this contact is a lead prospect rather than a buyer customer."
    )

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id=view_id, view_type=view_type, **options)
        user = self.env.user
        if user.crm_custom_permissions_enabled and not user.has_group('base.group_system'):
            if view_type == 'form':
                # Hide sensitive contact fields and tabs for restricted users
                for node in arch.xpath("//page[@name='sales_purchases'] | //page[@name='contact_addresses'] | //field[@name='email'] | //field[@name='phone'] | //field[@name='mobile'] | //field[@name='street'] | //field[@name='street2']"):
                    node.set('invisible', '1')
        return arch, view

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, **kwargs):
        user = self.env.user
        # Do not restrict superuser/admin or users without custom permissions
        if not self.env.su and user.crm_custom_permissions_enabled and not user.has_group('base.group_system'):
            if not self.env.context.get('skip_custom_crm_filter'):
                # Base allowed partners: user's partner and company partner
                allowed_partner_ids = list(filter(None, [user.partner_id.id, user.company_id.partner_id.id]))
                
                # Also allow partners linked to any CRM lead so record loading doesn't throw Access Error
                try:
                    leads_sudo = self.env['crm.lead'].sudo().search([])
                    lead_partners = leads_sudo.mapped('partner_id').ids
                    allowed_partner_ids.extend(lead_partners)
                except Exception:
                    pass

                prospect_domain = [
                    '|', ('x_is_lead_prospect', '=', True),
                    '|', ('id', 'in', allowed_partner_ids),
                    ('user_ids', '!=', False)
                ]
                domain = expression.AND([domain, prospect_domain])
        return super()._search(domain, offset=offset, limit=limit, order=order, **kwargs)
