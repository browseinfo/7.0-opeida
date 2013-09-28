# -*- coding: utf-8 -*-
##############################################################################
#
#    Manufacturing Subcontracting Process
#    Copyright (C) 2004-2010 Browse Info Pvt Ltd (<http://www.browseinfo.com>).
#    $autor:
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

import netsvc
from tools.translate import _
from osv import fields, osv

class order_line_expiry(osv.osv_memory):

   _name ='order.line.expiry'
   _description = 'sale order line expiry Report'
   _columns = {
        'partner_id': fields.many2one("res.partner", 'Partner'),
        'date': fields.datetime('Date'),
    }

   _defaults = {
        'date': fields.date.context_today,
    }

   def print_report(self, cr, uid, ids, context=None):
        """
         To get the date and print the report
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return: return report
        """
        if context is None:
            context = {}
        order_line_obj = self.pool.get('sale.order.line')
        partner_id = self.browse(cr, uid, ids, context=context)[0].partner_id
        date = self.browse(cr, uid, ids, context=context)[0].date
        print_ids = []
        line_ids =  order_line_obj.search(cr, uid, [('order_partner_id', '=', partner_id.id)], context=context)
        today = time.strftime('%Y-%m-%d')
        next_10th_date = datetime.strptime(today, '%Y-%m-%d') + relativedelta(days=10)
        next_date =  next_10th_date.strftime('%Y-%m-%d')
        
        for line in order_line_obj.browse(cr, uid, line_ids, context=context):
            if line.license_id:
                rdate = line.license_id.activation_end_date
                if today < rdate and rdate < next_date:
                    print_ids.append(line.id)
                    
        if not print_ids:
            raise osv.except_osv(_('Warring!'), _('There is no sale order product expiry line for this partner'))
        
        datas = {'ids': print_ids}
        res = self.read(cr, uid, ids, context=context)
        res = res and res[0] or {}
        res.update({'ids': datas['ids']})
        datas.update({'form': res})
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'order.line.expiry.report',
            'datas': datas,
       }

   def send_mail_partner(self, cr, uid, ids, context=None):
        """
         To get the date and print the report
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return: return report
        """
        if context is None:
            context = {}
        order_line_obj = self.pool.get('sale.order.line')
        partner_id = self.browse(cr, uid, ids, context=context)[0].partner_id
        date = self.browse(cr, uid, ids, context=context)[0].date
        print_ids = []
        line_ids =  order_line_obj.search(cr, uid, [('order_partner_id', '=', partner_id.id)], context=context)
        today = time.strftime('%Y-%m-%d')
        next_10th_date = datetime.strptime(today, '%Y-%m-%d') + relativedelta(days=10)
        next_date =  next_10th_date.strftime('%Y-%m-%d')
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'order_line_expiry', 'email_template_order_line_expiry')[1]
        
        for line in order_line_obj.browse(cr, uid, line_ids, context=context):
            if line.license_id:
                rdate = line.license_id.activation_end_date
                if today < rdate and rdate < next_date:
                    print_ids.append(line.id)
                    self.pool.get('email.template').send_mail(cr,uid,template_id,line.id,force_send=True)
                    
        if not print_ids:
            raise osv.except_osv(_('Warring!'), _('There is no sale order product expiry line for this partner'))
        
        return True

order_line_expiry()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
