# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


{
    'name': "Comptabilite analytique (activités / prestations)",

    'summary': """
        Comptabilite analytique (activités / prestations)
        """,

    'description': """
        Comptabilite analytique (activités / prestations)
    """,

    'author': "TECH-IT/DAMANSOFT",
    'website': "www.tech-it.ma",
    'category': 'Comptabilite',
    'version': '14.0',
    'depends': ['base', 'account', 'analytic', 'purchase_requisition'],
    'data': [
        'security/abc_groups.xml',
        'security/ir.model.access.csv',
        'data/prestation_sequence.xml',
        'views/account_view.xml',
        'views/analytic_view.xml',
        'views/invoice_view.xml',
        ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
}
