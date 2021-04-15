# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _


class res_partner(models.Model):
    _inherit = 'res.partner'

    # code = fields.Char(string="Code douane", required=True)

    @api.model
    def create(self, vals):
        res = super(res_partner, self).create(vals)
        if res.code and res.customer:
            processus_client = self.env['account.processus'].search([('client', '=', True)])
            if not processus_client:
                processus_client = self.env['account.processus'].create({'name': 'Processus client',
                                                                         'client': True,
                                                                         'code': 'CLIENT'})
            presta_id = self.env['account.prestation'].create({'name': res.name,
                                                               'code': res.code,
                                                               'code_externe': res.code,
                                                               'processus_id': processus_client[0].id,
                                                               'active': True
                                                               })
        return res


class account_processus(models.Model):
    _inherit = 'account.processus'

    client = fields.Boolean("Processus des clients")