# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, **kwargs):
        user = self.env.user
        # Do not restrict system/admin users or users without custom permissions
        if user.crm_custom_permissions_enabled and not user.has_group('base.group_system'):
            custom_domain = []
            if user.crm_lead_view_rule == 'own':
                custom_domain = ['|', ('user_id', '=', user.id), ('create_uid', '=', user.id)]
            elif user.crm_lead_view_rule == 'team':
                # Allow leads belonging to allowed teams OR leads they are responsible for/created
                custom_domain = [
                    '|', ('team_id', 'in', user.crm_allowed_team_ids.ids),
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

        # Trigger stage change emails
        if 'stage_id' in vals:
            for lead in self:
                stage = lead.stage_id
                if stage and stage.send_email_on_entry and stage.email_template_id:
                    stage.email_template_id.sudo().send_mail(lead.id, force_send=True)

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

        # Trigger stage change emails on creation
        for lead in leads:
            stage = lead.stage_id
            if stage and stage.send_email_on_entry and stage.email_template_id:
                stage.email_template_id.sudo().send_mail(lead.id, force_send=True)

        return leads

    def unlink(self):
        user = self.env.user
        if user.crm_custom_permissions_enabled and not user.has_group('base.group_system'):
            if not user.crm_lead_can_delete:
                raise UserError(_("Permission denied. Please contact your administrator."))
        return super().unlink()
