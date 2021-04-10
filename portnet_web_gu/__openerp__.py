# -*- coding: utf-8 -*-
{
    'name': 'Portnet GU',
    'version': '8.0',
    'description': """Interface ODOO GU Portnet""",
    'author': 'Leith Solutions',
    'website': 'www.leithsolutions.net',
    'depends': ['account','analytic','account_activity_prestation'],
    'data': [
        'security/ir.model.access.csv',
        'data/ops_sequence.xml',
        'views/portnet_edi.xml',
        'views/portnet_fs.xml',
        'views/portnet_web.xml',
        'views/portnet_doc_ops.xml',
        'views/portnet_client.xml',
        ],
    'demo': [],
    'test': [],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
