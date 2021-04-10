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

    'author': "Leith Solutions",
    'website': "www.leithsolutions.net",
    'category': 'Comptabilite',
    'version': '14.0',
    'depends': ['account','analytic','portnet_budget'],
    "images": ['static/description/banner.png'],
    'data': [
        'security/abc_groups.xml',
        'security/ir.model.access.csv',
        'data/prestation_sequence.xml',
        'views/account.xml',
        'views/activity_prestation.xml',
        'views/processus.xml',
        'views/analytic_key.xml',
        'views/attribut.xml',
        ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
}
