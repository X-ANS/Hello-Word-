# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _


class account_processus(models.Model):
    _name = 'account.processus'
    _rec_name = 'code'

    name = fields.Char(string=u'Description', required=True)
    code = fields.Char(string=u'Code', required=True)
    tax_exclude = fields.Boolean(string=u"Exclure prestations avec déficit")
