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
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        user = self.env.user
        if not self.env.su and user.crm_custom_permissions_enabled and not user.has_group('base.group_system'):
            if 'x_is_lead_prospect' in fields_list or not fields_list:
                res['x_is_lead_prospect'] = True
        return res

    @api.model_create_multi
    def create(self, vals_list):
        user = self.env.user
        if not self.env.su and user.crm_custom_permissions_enabled and not user.has_group('base.group_system'):
            for vals in vals_list:
                if 'x_is_lead_prospect' not in vals:
                    vals['x_is_lead_prospect'] = True
        return super().create(vals_list)

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
                # Check if this search is querying specific record IDs (e.g. reading partner_id of a crm.lead)
                has_id_filter = False
                if domain:
                    for leaf in domain:
                        if isinstance(leaf, (list, tuple)) and len(leaf) == 3 and leaf[0] == 'id':
                            has_id_filter = True
                            break

                # When listing/browsing contacts in Contacts app, restrict strictly to prospect contacts
                if not has_id_filter:
                    prospect_domain = [('x_is_lead_prospect', '=', True)]
                    domain = expression.AND([domain, prospect_domain])

        return super()._search(domain, offset=offset, limit=limit, order=order, **kwargs)
