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

class inactive_partner_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(inactive_partner_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
             'time': time,
             'do_line':self._do_line,
        })

    
    def _do_line(self,form):
        part_ids = form.get('ids')
        order_line_obj = self.pool.get('res.partner')
        res = []
        for line in order_line_obj.browse(self.cr,self.uid, part_ids):
            res.append({
                        'name': line.name or '', 
                        'phone': line.phone or '',
                        'mobile': line.mobile,
                        'email': line.email,
                        'fax': line.fax or '',
                        
                        })
        return res

report_sxw.report_sxw(
    'report.inactive.partner.report',
    'res.partner',
    'addons/inactive_partner_report/report/order_line_expiry.rml',
    parser=inactive_partner_report,
    header='external'
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
