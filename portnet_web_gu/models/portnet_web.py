# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class PortnetWeb(models.Model):
    _name = 'portnet.web'

    name = fields.Many2one('account.prestation', string=u'Prestation',required=True)
    num = fields.Float(string=u'Quantité',required=True)
    date = fields.Date(string=u"Date",required=True)
