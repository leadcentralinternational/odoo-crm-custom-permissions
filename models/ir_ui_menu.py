# -*- coding: utf-8 -*-
from odoo import api, models

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    def _filter_visible_menus(self):
        if self.env.context.get('skip_custom_crm_filter'):
            return super(IrUiMenu, self)._filter_visible_menus()

        user = self.env.user
        
        # System administrators bypass custom menu restrictions
        if user.crm_custom_permissions_enabled and not user.has_group('base.group_system'):
            sales_app_menu = self.env.ref('sale.sale_menu_root', raise_if_not_found=False)
            crm_app_menu = self.env.ref('crm.crm_menu_root', raise_if_not_found=False)
            
            crm_sales_menu = self.env.ref('crm.crm_menu_sales', raise_if_not_found=False)
            crm_report_menu = self.env.ref('crm.crm_menu_report', raise_if_not_found=False)
            crm_config_menu = self.env.ref('crm.crm_menu_config', raise_if_not_found=False)

            exclude_menus = self.env['ir.ui.menu']
            
            # 1. Always hide Sales App root menu
            if sales_app_menu:
                exclude_menus |= sales_app_menu

            # 2. Check CRM submenus based on Admin Options
            if user.crm_admin_options_enabled:
                if crm_sales_menu and not user.crm_show_menu_sales:
                    exclude_menus |= crm_sales_menu
                if crm_report_menu and not user.crm_show_menu_report:
                    exclude_menus |= crm_report_menu
                if crm_config_menu and not user.crm_show_menu_config:
                    exclude_menus |= crm_config_menu
            else:
                # If Admin Options is not checked, hide Configuration menu by default for non-admins
                if crm_config_menu:
                    exclude_menus |= crm_config_menu

            def is_excluded(menu):
                current = menu
                while current:
                    if current in exclude_menus:
                        return True
                    current = current.parent_id
                return False

            menu_env = self.with_context(skip_custom_crm_filter=True)

            candidate_menus = self
            if crm_app_menu:
                crm_branch = menu_env.search([('id', 'child_of', crm_app_menu.id)])
                candidate_menus = candidate_menus | crm_branch

            visible_menus = super(IrUiMenu, candidate_menus)._filter_visible_menus()

            # Re-include CRM Configuration branch if explicitly allowed in Admin Options
            if crm_app_menu and user.crm_admin_options_enabled and user.crm_show_menu_config and crm_config_menu:
                config_branch = menu_env.search([('id', 'child_of', crm_config_menu.id)])
                visible_menus |= config_branch

            # Always ensure CRM root app menu is visible if custom permissions are enabled
            if crm_app_menu:
                visible_menus |= crm_app_menu

            # Filter out excluded menus (Sales App, disabled CRM submenus)
            visible_menus = visible_menus.filtered(lambda m: not is_excluded(m))
            return visible_menus

        return super(IrUiMenu, self)._filter_visible_menus()


