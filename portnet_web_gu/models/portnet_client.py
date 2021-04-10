# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class PortnetClient(models.Model):
    _name = 'portnet.client'

    name = fields.Many2one('account.prestation', string=u'Compte client',required=True)
    code_client = fields.Char(related='name.code',string=u'Code client',readonly=True)
    num = fields.Float(string=u"Nombre d'opération",required=True)
    date = fields.Date(string=u"Date",required=True)
    client_categ_id = fields.Many2one('account.prestation', string=u'Catégorie client', required=True)