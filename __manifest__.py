# -*- coding: utf-8 -*-
{
    'name': 'CRM Custom Permissions',
    'version': '1.0',
    'category': 'Sales/CRM',
    'summary': 'Permisos personalizados y dinámicos para leads de CRM',
    'description': """
Módulo de Odoo para configurar de forma granular y dinámica los permisos de CRM (visibilidad, edición, eliminación, equipos de CRM y transiciones de etapas permitidas) directamente desde el formulario del usuario en Odoo.
    """,
    'author': 'Lead Central International',
    'depends': ['base', 'crm', 'sales_team'],
    'data': [
        'views/res_users_views.xml',
        'views/crm_stage_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
