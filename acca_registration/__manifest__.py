# -*- coding: utf-8 -*-
{
    'name': 'ACCA Registration',
    'version': '1.0',
    'summary': 'Manage Student ACCA Registrations and Web Form Portal',
    'description': """
        This module manages ACCA registration requests submitted by students
        via a public website web form, and lists them in the Odoo backend.
    """,
    'category': 'Uncategorized',
    'author': 'Antigravity AI',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/acca_registration_views.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'acca_registration/static/src/js/acca_list_controller.js',
            'acca_registration/static/src/xml/acca_list_buttons.xml',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
