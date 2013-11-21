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
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import netsvc
from tools.translate import _
from osv import fields, osv
from datetime import datetime,timedelta

class inactive_partner(osv.osv_memory):

    _name ='inactive.partner'
    _description = 'inactive partner Report'


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
        if not print_ids:
            raise osv.except_osv(_('Warring!'), _('There is no partner'))
        
        datas = {'ids': list_ids}
        res = self.read(cr, uid, ids, context=context)
        res = res and res[0] or {}
        res.update({'ids': datas['ids']})
        datas.update({'form': res})
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'inactive.partner.report',
            'datas': datas,
       }

inactive_partner()


class month_partner(osv.osv_memory):

    _name ='month.partner'
    _description = 'Partner in Month'
    _columns = {
        'period_id': fields.many2one('account.period', 'Period', required=True),
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
        partner_obj = self.pool.get('res.partner')
        partner_ids =  partner_obj.search(cr, uid, [], context=context)
        period_id = self.browse(cr, uid, ids, context=context)[0].period_id
        date_st = datetime.strptime(period_id.date_start, '%Y-%m-%d').date()
        date_end = datetime.strptime(period_id.date_stop, '%Y-%m-%d').date()
        part_ids = []
        
        for partner in partner_obj.browse(cr, uid, partner_ids, context=context):
            cr.execute('SELECT create_date FROM res_partner WHERE id=%s', (partner.id,))
            res = cr.fetchone()
            if res[0]:
                dt = res[0].split()
                create_date = datetime.strptime(dt[0], '%Y-%m-%d').date()
                if date_st < create_date and  create_date <date_end:
                    part_ids.append(partner.id)
      
        if not part_ids:
            raise osv.except_osv(_('Warring!'), _('There is no partner'))
        
        datas = {'ids': part_ids}
        res = self.read(cr, uid, ids, context=context)
        res = res and res[0] or {}
        res.update({'ids': datas['ids']})
        datas.update({'form': res})
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'month.partner.report',
            'datas': datas,
       }

month_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
