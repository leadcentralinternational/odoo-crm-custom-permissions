# -*- coding: utf-8 -*-
from odoo import models

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super().session_info()
        user = self.env.user
        result['crm_custom_permissions_enabled'] = bool(
            user.crm_custom_permissions_enabled and not user.has_group('base.group_system')
        )
        return result
