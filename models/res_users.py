# -*- coding: utf-8 -*-
from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    crm_custom_permissions_enabled = fields.Boolean(
        string='Enable Custom CRM Permissions',
        default=False,
        help='If checked, the custom checklist permissions below will be applied to this user instead of general groups.'
    )
    crm_lead_view_rule = fields.Selection([
        ('own', 'Only Own Leads (Created or Assigned)'),
        ('team', 'Only Leads belonging to Selected Teams'),
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
    crm_allowed_team_ids = fields.Many2many(
        'crm.team',
        'res_users_crm_team_rel',
        'user_id',
        'team_id',
        string='Allowed CRM Teams',
        help='CRM teams this user is allowed to access leads from.'
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
        string='Sales',
        default=True,
        help='Check to show the Sales/Pipeline menu in CRM.'
    )
    crm_show_menu_report = fields.Boolean(
        string='Reporting',
        default=True,
        help='Check to show the Reporting menu in CRM.'
    )
    crm_show_menu_config = fields.Boolean(
        string='Configuration',
        default=True,
        help='Check to show the Configuration menu in CRM.'
    )
