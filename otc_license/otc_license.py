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
import time
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta

from openerp.osv import osv, fields
from openerp import tools, SUPERUSER_ID
from openerp.tools.translate import _
from openerp import netsvc


class otc_license(osv.osv):
    _name = 'otc.license'
    _rec_name = 'otc'

    def _check_sold(self, cr, uid, ids):
        for otc in self.browse(cr, uid, ids):
            otc_ids = self.search(cr, uid, [('sold', '=', True)])
            if otc_ids:
                return False
        return True

    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
        'otc': fields.char('OTC', help='OTC', required=True),
        'activation_start_date': fields.date('Activation Start Date', help="Start Date Of Activation."),
        'activation_end_date': fields.date('Activation End Date', help="End Date Of Activation."),
        'expiry_date': fields.date('Expiry Date', help="Expiry Date."),
        'runtime': fields.char('Runtime', help='12 months validation'),
        'users': fields.char('Number of User', size=64),
        'vso_id':fields.many2one('stock.production.lot','VSO Number',  select=True, domain="[('product_id','=',product_id)]"),
        'sold': fields.boolean('sold'),
        
    }
    _defaults = {
        'sold': False,
    }

    _constraints = [
        (_check_sold, 'You can not sell OTC license which already sold!', ['otc','product_id']),
    ]

    def on_change_product_id(self, cr, uid, ids, product_id, context=None):
        values = {}
        if product_id:
            product_obj = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            values = {
                'runtime' : product_obj.validity,
                'users'  : product_obj.users,
            }
        return {'value' : values}

otc_license()


class sale_order(osv.osv):
    _inherit = 'sale.order'

    def action_button_confirm(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        otc_obj = self.pool.get('otc.license')
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'sale.order', ids[0], 'order_confirm', cr)
        for sale in self.browse(cr, uid, ids, context):
           for line in sale.order_line:
               for otc in line.otc_lines:
                   if otc:
                       otc_obj.write(cr, uid, [otc.id], {'sold':True}, context)
                        
        # redisplay the record as a sales order
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'view_order_form')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sales Order'),
            'res_model': 'sale.order',
            'res_id': ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }

sale_order()
#
#    def do_run_scheduler(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
#        """Scheduler for Task reminder
#        @param self: The object pointer
#        @param cr: the current row, from the database cursor,
#        @param uid: the current user's ID for security checks,
#        @param ids: List of calendar alarm's IDs.
#        @param use_new_cursor: False or the dbname
#        @param context: A standard dictionary for contextual values
#        """
#        if context is None:
#            context = {}
#        mail_mail = self.pool.get('mail.mail')
#        line_ids = []
#        order_ids = self.search(cr, uid, [('state', 'not in', ('draft','sent', 'done'))], context=context)
#        mail_to = ""
#        mail_ids = []
#
#        today = time.strftime('%Y-%m-%d')
#        next_10th_date = datetime.strptime(today, '%Y-%m-%d') + relativedelta(days=30)
#        next_date =  next_10th_date.strftime('%Y-%m-%d')
#        
#        for order in self.browse(cr, uid, order_ids, context=context):
#            for line in order.order_line:
#                if line.license_id:
#                    rdate = line.license_id.activation_end_date
#                    if today < rdate and rdate < next_date:
#                        line_ids.append(line.id)
#
#
#            if line_ids:
#                sub = '[sale product Reminder] %s - %s ' % (order.partner_id.name, order.name)
#                body = """<pre>
#Hello %s,
#
#Just a friendly reminder you , Your sale product line has been expired soon. 
#
#
#From:
#      %s
#
#----
#%s
#</pre>
#"""  % (order.partner_id.name,order.user_id.name, order.user_id.signature)
#                mail_to = order.partner_id.email
#                if mail_to:
#                    vals = {
#                        'state': 'outgoing',
#                        'subject': sub,
#                        'body_html': body,
#                        'email_to': mail_to,
#                        'email_from': tools.config.get('email_from', mail_to),
#                    }
#                    
#                    mail_ids.append(mail_mail.create(cr, uid, vals, context=context))
#                    mail_mail.send(cr, uid, mail_ids, auto_commit=True, context=context)
#        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
