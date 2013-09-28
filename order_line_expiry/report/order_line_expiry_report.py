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
import datetime
from report import report_sxw

class order_line_expiry_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(order_line_expiry_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
             'time': time,
             'do_line':self._do_line,
             'do_data': self._do_data,
             'sum_total': self.sum_total,
        })

    def _do_data(self,form):
        so_ids = form.get('ids')
        order_line_obj = self.pool.get('sale.order.line')
        res = []
        for line in order_line_obj.browse(self.cr,self.uid, so_ids):
            res.append({
                        'name': line.order_partner_id.name or '',
                        'street': line.order_partner_id.street or '',
                        'street2': line.order_partner_id.street2 or '',
                        'zip': line.order_partner_id .zip,
                        'state_id': line.order_partner_id.state_id.name or '',
                        'country_id':line.order_partner_id.country_id.name or '',
                        
                        })
        return res
    
    def sum_total(self, form):
        return self.regi_total
        
    def _do_line(self,form):
        so_ids = form.get('ids')
        order_line_obj = self.pool.get('sale.order.line')
        res = []
        self.regi_total = 0.0
        for line in order_line_obj.browse(self.cr,self.uid, so_ids):
            res.append({
                        'product_id': line.product_id.name or '', 
                        'order_id': line.order_id.name or '',
                        'expiry_date': line.license_id.activation_end_date,
                        'qty': line.product_uom_qty,
                        'uom': line.product_uom.name or '',
                        'price': line.price_unit,
                        'subtotal': line.price_subtotal,
                        
                        })
            self.regi_total += line.price_subtotal
        return res

report_sxw.report_sxw(
    'report.order.line.expiry.report',
    'sale.order.line',
    'addons/order_line_expiry/report/order_line_expiry.rml',
    parser=order_line_expiry_report,
    header='external'
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
