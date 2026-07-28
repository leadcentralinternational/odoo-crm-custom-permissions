# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    crm_custom_permissions_enabled = fields.Boolean(
        string='Enable Custom CRM Permissions',
        default=False,
        help='If checked, the custom checklist permissions below will be applied to this user instead of general groups.'
    )
    crm_lead_view_rule = fields.Selection([
        ('own', 'Only Own Leads (Created or Assigned)'),
        ('team', 'Only Leads belonging to Assigned Teams'),
        ('all', 'All CRM Leads')
    ], string='Lead Visibility Level', default='all', help='Defines what leads this user is allowed to search and view.')
    
    crm_lead_can_edit = fields.Boolean(
        string='Can Edit CRM Leads',
        default=True,
        help='Uncheck to restrict this user to read-only access for CRM leads.'
    )
    crm_lead_can_delete = fields.Boolean(
        string='Can Delete CRM Leads',
        default=False,
        help='Check to allow this user to delete CRM leads.'
    )
    crm_can_create_stages = fields.Boolean(
        string='Can Create Stages',
        default=False,
        help='Check to allow this user to create CRM stages and see the + Stage option.'
    )
    crm_allowed_stage_ids = fields.Many2many(
        'crm.stage',
        'res_users_crm_stage_rel',
        'user_id',
        'stage_id',
        string='Allowed CRM Stages',
        help='CRM stages this user is allowed to move leads into or manage.'
    )

    # Admin Options for CRM menus
    crm_admin_options_enabled = fields.Boolean(
        string='Admin Options',
        default=False,
        help='If checked, allows filtering access to CRM submenus (Sales, Reporting, Configuration).'
    )
    crm_show_menu_sales = fields.Boolean(
        string='CRM Pipeline / Sales Submenu',
        default=True,
        help='Check to show the Sales/Pipeline menu inside CRM (My Pipeline, Leads, etc.).'
    )
    crm_show_menu_report = fields.Boolean(
        string='CRM Reporting Submenu',
        default=True,
        help='Check to show the Reporting menu inside CRM.'
    )
    crm_show_menu_config = fields.Boolean(
        string='CRM Configuration Submenu',
        default=True,
        help='Check to show the Configuration menu inside CRM.'
    )

    def _ensure_crm_base_group(self, vals):
        # Enable multi-team membership natively in Odoo
        ICPSudo = self.env['ir.config_parameter'].sudo()
        if not ICPSudo.get_param('sales_team.membership_multi'):
            ICPSudo.set_param('sales_team.membership_multi', 'True')

        group_salesman = self.env.ref('sales_team.group_sale_salesman', raise_if_not_found=False)
        if not group_salesman:
            return
        for user in self:
            enabled = vals.get('crm_custom_permissions_enabled', user.crm_custom_permissions_enabled)
            if enabled and group_salesman not in user.groups_id:
                user.sudo().write({'groups_id': [(4, group_salesman.id)]})

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        for user, vals in zip(users, vals_list):
            if vals.get('crm_custom_permissions_enabled'):
                user._ensure_crm_base_group(vals)
        return users

    def write(self, vals):
        res = super().write(vals)
        if 'crm_custom_permissions_enabled' in vals:
            self._ensure_crm_base_group(vals)
        return res

