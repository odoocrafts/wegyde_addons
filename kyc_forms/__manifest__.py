# -*- coding: utf-8 -*-
{
    'name': 'KYC Forms',
    'version': '1.0',
    'summary': 'Manage Student Admission KYC Forms and Public Portal',
    'description': """
        Manage WeGyde Student Admission & KYC forms submitted through the public website portal.
    """,
    'category': 'Education',
    'author': 'Antigravity AI',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/kyc_form_views.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'kyc_forms/static/src/js/kyc_list_controller.js',
            'kyc_forms/static/src/xml/kyc_list_buttons.xml',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
