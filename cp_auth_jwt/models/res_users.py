# -*- coding: utf-8 -*-

from odoo import fields, models, registry, tools
from odoo.exceptions import AccessDenied
from openerp.http import request

from .. import utils

class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    
    jwt_key = fields.Char('jwt Key', size=utils.KEY_LENGTH, readonly=True, copy=False)
    #user_cin = fields.Char('CIN')
    login_date = fields.Datetime('Last login')


    @classmethod
    def _login(cls, db, login, password):
        result = super(ResUsersInherit, cls)._login(db, login, password)
        if result:
            return result
        else:
            with registry(db).cursor() as cr:
                cr.execute("""UPDATE res_users
                                SET login_date=now() AT TIME ZONE 'UTC'
                                WHERE login=%s AND jwt_key=%s AND active=%s RETURNING id""",
                           (tools.ustr(login), tools.ustr(password), True))
                # beware: record cache may be invalid
                res = cr.fetchone()
                cr.commit()
                return res[0] if res else False

    # @classmethod
    def _check_credentials(self, password):
        cr = self.pool.cursor()
        uid = self.id
        try:
            return super(ResUsersInherit, self)._check_credentials(password)
        except AccessDenied as e:
            cr.execute('''SELECT COUNT(1)
                            FROM res_users
                           WHERE id=%s
                             AND jwt_key=%s
                             AND active=%s''',
                       (int(uid), password, True))
            if not cr.fetchone()[0]:
                raise e
