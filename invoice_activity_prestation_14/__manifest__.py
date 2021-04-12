# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


{
    'name': "Invoice line with activity / prestation",

    'summary': """
        Invoice line with activity / prestation
        """,

    'description': """
        Invoice line with activity / prestation
    """,

    'author': "Leith Solutions",
    'website': "www.leithsolutions.net",
    'category': 'Comptabilite',
    'version': '14.0',
    'depends': ['base','account','account_activity_prestation_14'],
    'data': [
        'views/invoice_view.xml',
        ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'active': False,
}
