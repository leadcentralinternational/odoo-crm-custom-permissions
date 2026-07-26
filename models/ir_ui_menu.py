# -*- coding: utf-8 -*-
from odoo import models

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    def _filter_visible_menus(self):
        # Odoo 18 calls this method on the menu recordset without arguments.
        menus = super()._filter_visible_menus()
        
        user = self.env.user
        # System administrators bypass custom menu restrictions
        if user.crm_custom_permissions_enabled and user.crm_admin_options_enabled and not user.has_group('base.group_system'):
            # Fetch CRM submenu records
            sales_menu = self.env.ref('crm.crm_menu_sales', raise_if_not_found=False)
            report_menu = self.env.ref('crm.crm_menu_report', raise_if_not_found=False)
            config_menu = self.env.ref('crm.crm_menu_config', raise_if_not_found=False)
            
            exclude_menus = self.env['ir.ui.menu']
            
            if sales_menu and not user.crm_show_menu_sales:
                exclude_menus |= sales_menu
            if report_menu and not user.crm_show_menu_report:
                exclude_menus |= report_menu
            if config_menu and not user.crm_show_menu_config:
                exclude_menus |= config_menu
                
            if exclude_menus:
                # Helper function to check if a menu or any of its parent menus is in exclude_menus
                def is_excluded(menu):
                    current = menu
                    while current:
                        if current in exclude_menus:
                            return True
                        current = current.parent_id
                    return False
                
                menus = menus.filtered(lambda m: not is_excluded(m))
                
        return menus
