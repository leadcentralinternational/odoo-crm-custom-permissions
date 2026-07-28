# -*- coding: utf-8 -*-
from odoo import api, models

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    def _filter_visible_menus(self):
        visible_menus = super(IrUiMenu, self)._filter_visible_menus()
        user = self.env.user

        # Apply custom permissions for non-admin users with custom permissions enabled
        if user.crm_custom_permissions_enabled and not user.has_group('base.group_system'):
            sales_app_menu = self.env.ref('sale.sale_menu_root', raise_if_not_found=False)
            crm_sales_menu = self.env.ref('crm.crm_menu_sales', raise_if_not_found=False)
            crm_report_menu = self.env.ref('crm.crm_menu_report', raise_if_not_found=False)
            crm_config_menu = self.env.ref('crm.crm_menu_config', raise_if_not_found=False)
            crm_pipeline_menu = self.env.ref('crm.menu_crm_opportunities', raise_if_not_found=False)

            exclude_menus = self.env['ir.ui.menu']

            # 1. Always hide Sales App root menu
            if sales_app_menu:
                exclude_menus |= sales_app_menu

            # 2. Check CRM submenus based on Admin Options
            if user.crm_admin_options_enabled:
                if crm_report_menu and not user.crm_show_menu_report:
                    exclude_menus |= crm_report_menu
                if crm_config_menu and not user.crm_show_menu_config:
                    exclude_menus |= crm_config_menu
                if crm_sales_menu and not user.crm_show_menu_sales:
                    # Exclude extra submenus of Sales BUT keep My Pipeline (crm_pipeline_menu)
                    sales_subs = self.env['ir.ui.menu'].search([('parent_id', '=', crm_sales_menu.id)])
                    for sub in sales_subs:
                        if crm_pipeline_menu and sub != crm_pipeline_menu:
                            exclude_menus |= sub
            else:
                # If Admin Options is disabled, hide Configuration menu by default
                if crm_config_menu:
                    exclude_menus |= crm_config_menu

            if exclude_menus:
                def is_excluded(menu):
                    # Never exclude the main CRM Pipeline menu
                    if crm_pipeline_menu and menu == crm_pipeline_menu:
                        return False
                    current = menu
                    while current:
                        if current in exclude_menus:
                            return True
                        current = current.parent_id
                    return False

                visible_menus = visible_menus.filtered(lambda m: not is_excluded(m))

        return visible_menus


