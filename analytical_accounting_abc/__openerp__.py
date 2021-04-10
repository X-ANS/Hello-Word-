# -*- coding: utf-8 -*-
{
    'name': 'Comptabilite analytique (ABC)',
    'version': '8.0',
    'description': """Comptabilite analytique (ABC)""",
    'author': 'LEITH SOLUTION',
    'website': 'www.leithsolutiosn.net',
    'depends': ['account','analytic','account_activity_prestation', 'timesheet_account'],
    'data': [
        'security/ir.model.access.csv',
        'views/analytical.xml',
        ],
    'demo': [],
    'test': [],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
