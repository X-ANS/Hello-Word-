# -*- coding: utf-8 -*-
{
    'name': "JWT CASH PLUS",

    'summary': """
    Module d'integration JWT
    """,

    'description': """
        Module d'integration JWT
    """,

    'author': "Ahmed LAHLOU",
    'website': "http://alahlou.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'tko_web_sessions_management'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo.xml',
    ],
}