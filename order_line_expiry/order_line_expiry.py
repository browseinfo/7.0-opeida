# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp import netsvc
from openerp.tools.translate import _


class sale_order(osv.osv):
    _inherit = 'sale.order'

    def action_cancel(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        mail_mail = self.pool.get('mail.mail')
        mail_ids = []
        if context is None:
            context = {}
        sale_order_line_obj = self.pool.get('sale.order.line')
        user = self.pool.get('res.users').browse(cr, uid, [1], context=context)[0]
        for sale in self.browse(cr, uid, ids, context=context):
            sub = '[Sale Order Cancel Reminder] %s - %s ' % (sale.partner_id.name, sale.name)
            body = """<pre>
Hello,

Sale order %s has been canceled by this user %s


From:
      %s

----
%s
</pre>
"""  % (sale.name,sale.user_id.name,sale.user_id.name, sale.user_id.signature)
            mail_ids.append(mail_mail.create(cr, uid, {
                    'email_from': sale.user_id.email,
                    'email_to': user.email,
                    'subject': sub,
                    'body_html': body}, context=context))
            mail_mail.send(cr, uid, mail_ids, auto_commit=True, context=context)
            for inv in sale.invoice_ids:
                if inv.state not in ('draft', 'cancel'):
                    raise osv.except_osv(
                        _('Cannot cancel this sales order!'),
                        _('First cancel all invoices attached to this sales order.'))
            for r in self.read(cr, uid, ids, ['invoice_ids']):
                for inv in r['invoice_ids']:
                    wf_service.trg_validate(uid, 'account.invoice', inv, 'invoice_cancel', cr)
            sale_order_line_obj.write(cr, uid, [l.id for l in  sale.order_line],
                    {'state': 'cancel'})
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True

sale_order()

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    _columns = {
        'user_id': fields.many2one('res.users', 'User'),
    }
    _defaults = {
        'user_id': lambda self, cr, uid, ctx: uid
    }
    
sale_order_line()