{
    'name': 'Custom Commission',
    'version': '1.0',
    'category': 'Sales',
    'author': 'Your Name',
    'depends': ['base', 'sale_management', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/commission_view.xml',
        'views/partner_view.xml',
        'views/commission_menu.xml',
        'report/commission_report.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
}
