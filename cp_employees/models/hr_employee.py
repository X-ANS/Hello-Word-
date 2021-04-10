# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models
import xmlrpclib


class Employee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def create(self, vals):
        new_record = super(Employee, self).create(vals)
        self.synchronize_employees(new_record)
        return new_record

    @api.model
    def synchronize_employees(self, rec):
        url_db = "https://erp.cashplus.ma"
        db = 'erp'
        username_db = 'admin@mobilab.ma'
        password_db = 'T5u[3Di4Y$yV&2k'
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url_db))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url_db))
        uid_db = common.authenticate(db, username_db, password_db, {})

        new_employee = models.execute_kw(db, uid_db, password_db, 'hr.employee', 'create', [
            {
                'name': rec['name'],
                'work_email': rec['work_email'],
            }])
