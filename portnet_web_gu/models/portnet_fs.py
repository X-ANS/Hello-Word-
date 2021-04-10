# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class PortnetFS(models.Model):
    _name = 'portnet.fs'

    name = fields.Many2one('account.prestation', string=u'Prestation',required=True)
    num = fields.Float(string=u'Nombre de FS',required=True)
    date = fields.Date(string=u"Date",required=True)
