# -*- coding: utf-8 -*-
{
    'name': 'Comptabilite analytique (activités / prestations)',
    'version': '8.0',
    'description': """Comptabilite analytique (activités / prestations)""",
    'author': 'Leith Solutions',
    'website': 'www.leithsolutions.net',
    'depends': ['account','analytic','portnet_budget'],
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
    'demo': [],
    'test': [],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
