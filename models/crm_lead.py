# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression

_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    x_prospect_name = fields.Char(string="Prospect Name")
    x_prospect_phone = fields.Char(string="Phone")
    x_prospect_mobile = fields.Char(string="Mobile")
    x_prospect_email = fields.Char(string="Email")
    x_prospect_street = fields.Char(string="Address")
    x_prospect_city = fields.Char(string="City")
    x_prospect_notes = fields.Text(string="Prospect Notes")

    def _sync_prospect_partner(self):
        # Do not automatically create or assign lead.partner_id from prospect details.
        # partner_id represents the Cliente Comprador / Portal Client and should remain
        # unassigned until an Administrator manually selects a buyer partner.
        pass

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type='form', **options):
        key = super()._get_view_cache_key(view_id=view_id, view_type=view_type, **options)
        user = self.env.user
        return key + (user.crm_custom_permissions_enabled, user.crm_can_create_stages)

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id=view_id, view_type=view_type, **options)
        user = self.env.user
        if user.crm_custom_permissions_enabled and not user.has_group('base.group_system'):
            if view_type == 'kanban':
                if not user.crm_can_create_stages:
                    arch.set('group_create', 'false')
                    arch.set('quick_create', 'false')
                for node in arch.xpath("//field[@name='expected_revenue'] | //field[@name='partner_id'] | //field[@name='recurring_revenue'] | //field[@name='recurring_plan']"):
                    node.set('invisible', '1')
            elif view_type == 'form':
                fields_to_hide = {
                    'partner_id', 'email_from', 'phone', 'mobile',
                    'expected_revenue', 'probability', 'recurring_revenue',
                    'recurring_plan', 'automated_probability'
                }
                for field_node in arch.xpath("//field"):
                    if field_node.get('name') in fields_to_hide:
                        field_node.set('invisible', '1')
                for label_node in arch.xpath("//label[@for='expected_revenue'] | //label[@for='probability']"):
                    label_node.set('invisible', '1')
                for h2 in arch.xpath("//h2"):
                    if h2.xpath(".//field[@name='expected_revenue']") or h2.xpath(".//field[@name='probability']"):
                        h2.set('invisible', '1')
                for node in arch.xpath("//div[@id='probability'] | //button[@name='action_set_automated_probability']"):
                    node.set('invisible', '1')

                # Hide non-prospect tabs (e.g. Extra Information) for restricted users
                for page in arch.xpath("//page"):
                    page_name = page.get('name')
                    if page_name and page_name not in ('prospect_page', 'internal_notes'):
                        page.set('invisible', '1')
        return arch, view

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, **kwargs):
        user = self.env.user
        # Do not restrict system/admin users or users without custom permissions
        if user.crm_custom_permissions_enabled and not user.has_group('base.group_system'):
            custom_domain = []
            if user.crm_lead_view_rule == 'own':
                custom_domain = ['|', ('user_id', '=', user.id), ('create_uid', '=', user.id)]
            elif user.crm_lead_view_rule == 'team':
                user_teams = self.env['crm.team'].search(['|', ('user_id', '=', user.id), ('member_ids', 'in', [user.id])])
                custom_domain = [
                    '|', ('team_id', 'in', user_teams.ids),
                    '|', ('user_id', '=', user.id), ('create_uid', '=', user.id)
                ]
            domain = expression.AND([domain, custom_domain])
        return super()._search(domain, offset=offset, limit=limit, order=order, **kwargs)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True, **kwargs):
        user = self.env.user
        result = super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy, **kwargs)
        
        if user.crm_custom_permissions_enabled and not user.has_group('base.group_system'):
            if groupby and groupby[0] == 'stage_id':
                allowed_stage_ids = user.crm_allowed_stage_ids.ids
                filtered_result = []
                for group in result:
                    stage_val = group.get('stage_id')
                    if stage_val:
                        stage_id = stage_val[0] if isinstance(stage_val, tuple) else stage_val
                        if stage_id in allowed_stage_ids:
                            filtered_result.append(group)
                    else:
                        filtered_result.append(group)
                return filtered_result
        return result

    def write(self, vals):
        user = self.env.user
        if user.crm_custom_permissions_enabled and not user.has_group('base.group_system'):
            # Check general editing permissions
            if not user.crm_lead_can_edit:
                raise UserError(_("Permission denied. Please contact your administrator."))
            
            # Check stage transitions
            if 'stage_id' in vals:
                allowed_stages = user.crm_allowed_stage_ids.ids
                if vals['stage_id'] not in allowed_stages:
                    raise UserError(_("Permission denied. Please contact your administrator."))
                    
        res = super().write(vals)

        prospect_fields = {'x_prospect_name', 'x_prospect_phone', 'x_prospect_mobile', 'x_prospect_email', 'x_prospect_street', 'x_prospect_city', 'x_prospect_notes'}
        if prospect_fields.intersection(vals.keys()):
            self._sync_prospect_partner()

        # Trigger stage change emails
        if 'stage_id' in vals:
            for lead in self:
                stage = lead.stage_id
                if stage and stage.send_email_on_entry and stage.email_template_id:
                    try:
                        stage.email_template_id.sudo().send_mail(lead.id, force_send=True)
                    except Exception as e:
                        _logger.warning("Failed to send stage entry email for lead %s (stage %s): %s", lead.id, stage.name, e)

        return res

    @api.model_create_multi
    def create(self, vals_list):
        user = self.env.user
        if user.crm_custom_permissions_enabled and not user.has_group('base.group_system'):
            if not user.crm_lead_can_edit:
                raise UserError(_("Permission denied. Please contact your administrator."))
                
            for vals in vals_list:
                if 'stage_id' in vals:
                    if vals['stage_id'] not in user.crm_allowed_stage_ids.ids:
                        raise UserError(_("Permission denied. Please contact your administrator."))
                        
        leads = super().create(vals_list)
        leads._sync_prospect_partner()

        # Trigger stage change emails on creation
        for lead in leads:
            stage = lead.stage_id
            if stage and stage.send_email_on_entry and stage.email_template_id:
                try:
                    stage.email_template_id.sudo().send_mail(lead.id, force_send=True)
                except Exception as e:
                    _logger.warning("Failed to send stage entry email for lead %s (stage %s): %s", lead.id, stage.name, e)

        return leads

    def unlink(self):
        user = self.env.user
        if user.crm_custom_permissions_enabled and not user.has_group('base.group_system'):
            if not user.crm_lead_can_delete:
                raise UserError(_("Permission denied. Please contact your administrator."))
        return super().unlink()
