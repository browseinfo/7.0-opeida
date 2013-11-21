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



class sale_order(osv.osv):
    _inherit = 'sale.order'


    def run_scheduler_partner_inactive(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
        """Scheduler for Task reminder
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user's ID for security checks,
        @param ids: List of calendar alarm's IDs.
        @param use_new_cursor: False or the dbname
        @param context: A standard dictionary for contextual values
        """
        print "hello======================"
        if context is None:
            context = {}
        mail_mail = self.pool.get('mail.mail')
        line_ids = []
#        order_ids = self.search(cr, uid, [('state', 'not in', ('draft','sent', 'done'))], context=context)
        mail_to = ""
        mail_ids = []

#         today = time.strftime('%Y-%m-%d')
#         next_10th_date = datetime.strptime(today, '%Y-%m-%d') + relativedelta(days=30)
#         next_date =  next_10th_date.strftime('%Y-%m-%d')
        
        partner_obj = self.pool.get('res.partner')
        partner_ids =  partner_obj.search(cr, uid, [('customer', '=', True)], context=context)
        current_date = datetime.today().strftime('%Y-%m-%d')
        date = (datetime.today() - relativedelta(months=+1,day=1,days=-1)).strftime('%Y-%m-%d')
        print_ids = []
        for partner in partner_obj.browse(cr, uid, partner_ids, context=context):
            for sale in partner.sale_order_ids:
                if date < sale.date_order and  sale.date_order < current_date:
                    print_ids.append(partner.id)
        
        list_ids = []
        list_ids = list(set(partner_ids)-set(print_ids))


        if line_ids:
                sub = '[Inactive Partner Remainder] %s  ' % (partner.id)
                body = """<pre>
Hello %s,

Just a friendly reminder you , These are the Inactive Partner For Last Month. 


From:
      %s

%s
</pre>
"""  % (partner.name,partner.user_id.name, partner.user_id.signature)
                mail_to = SUPERUSER_ID.email
                print "mail to ===============",mail_to
                if mail_to:
                    vals = {
                        'state': 'outgoing',
                        'subject': sub,
                        'body_html': body,
                        'email_to': mail_to,
                        'email_from': tools.config.get('email_from', mail_to),
                    }
                    
                    mail_ids.append(mail_mail.create(cr, uid, vals, context=context))
                    mail_mail.send(cr, uid, mail_ids, auto_commit=True, context=context)
        return True

sale_order()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
