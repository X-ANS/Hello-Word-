# -*- coding: utf-8 -*-

{
    "name": "TimeSheet Activity / Prestation",
    "version": "1.1",
    "depends": ['hr_timesheet','hr_timesheet_sheet','timesheet_account'],
    "author": "PORTNET - Mouad Ghandi",
    'website': 'https://portail.portnet.ma/',
    "category": "Human Resources, Analytic Accounting",
    "description": "",
    'data': [
        'views/hr_timesheet_sheet_view.xml',
        'views/hr_timesheet_view.xml',
        'views/hr_employee_views.xml',
        'wizards/sync_analytic_parameter_wizard.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
