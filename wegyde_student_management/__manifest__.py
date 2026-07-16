{
    'name': 'Wegyde Students Addons',
    'version': '17.0.1.0.0',
    'category': 'Education',
    'summary': 'Manage students from CRM leads',
    'description': """
        Student Management System
        - Create students from CRM leads
        - Manage student information
        - Track academic records
        - Store contact details
    """,
    'depends': ['crm', 'student_management', ],
    'data': [

        'views/student.xml',
        'views/crm.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'web_icon': "student_management,static/description/icon.png",
}
