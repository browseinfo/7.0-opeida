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
#import datetime
import time
from datetime import datetime,timedelta
from openerp.osv import osv, fields
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta


class res_partner_partner(osv.osv):
     _name = 'res.partner.partner'
     
     _columns = {
        'name': fields.char('Name', size=128, required=True, select=True),
        'street': fields.char('Street', size=128),
        'street2': fields.char('Street2', size=128),
        'zip': fields.char('Zip', change_default=True, size=24),
        'city': fields.char('City', size=128),
        'state_id': fields.many2one("res.country.state", 'State'),
        'country_id': fields.many2one('res.country', 'Country'),
        'email': fields.char('Email', size=240),
        'phone': fields.char('Phone', size=64),
        'fax': fields.char('Fax', size=64),
        'mobile': fields.char('Mobile', size=64),
        'website': fields.char('Website', size=64, help="Website of Partner or Company"),
        'partner_id': fields.many2one("res.partner", 'Partner'),

    }
res_partner_partner()

class res_partner(osv.osv):
     _inherit = 'res.partner'
     
     _columns = {
        'partner_partner_id': fields.many2one("res.partner.partner", 'Customer'),
        'resaler': fields.boolean('Resaler'),

    }
res_partner() 

class sale_order(osv.osv):
     _inherit = 'sale.order'

     _columns = {
        'partner_partner_id': fields.many2one("res.partner.partner", 'Customer'),
        'email': fields.char('Email', size=240),
     }

     def on_change_partner_partner_id(self, cr, uid, ids, partner_partner_id, context=None):
        values = {}
        if partner_partner_id:
            partner_partner = self.pool.get('res.partner.partner').browse(cr, uid, partner_partner_id, context=context)
            values = {
                'email' : partner_partner.email,
            }
        return {'value' : values}

     def _prepare_invoice(self, cr, uid, order, lines, context=None):
        """Prepare the dict of values to create the new invoice for a
           sales order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record order: sale.order record to invoice
           :param list(int) line: list of invoice line IDs that must be
                                  attached to the invoice
           :return: dict of value to create() the invoice
        """
        if context is None:
            context = {}
        journal_ids = self.pool.get('account.journal').search(cr, uid,
            [('type', '=', 'sale'), ('company_id', '=', order.company_id.id)],
            limit=1)
        if not journal_ids:
            raise osv.except_osv(_('Error!'),
                _('Please define sales journal for this company: "%s" (id:%d).') % (order.company_id.name, order.company_id.id))
        invoice_vals = {
            'name': order.client_order_ref or '',
            'origin': order.name,
            'type': 'out_invoice',
            'reference': order.client_order_ref or order.name,
            'account_id': order.partner_id.property_account_receivable.id,
            'partner_id': order.partner_invoice_id.id,
            'journal_id': journal_ids[0],
            'invoice_line': [(6, 0, lines)],
            'currency_id': order.pricelist_id.currency_id.id,
            'comment': order.note,
            'payment_term': order.payment_term and order.payment_term.id or False,
            'fiscal_position': order.fiscal_position.id or order.partner_id.property_account_position.id,
            'date_invoice': context.get('date_invoice', False),
            'company_id': order.company_id.id,
            'user_id': order.user_id and order.user_id.id or False,
            'partner_partner_id': order.partner_partner_id and order.partner_partner_id.id or False,
        }

        # Care for deprecated _inv_get() hook - FIXME: to be removed after 6.1
        invoice_vals.update(self._inv_get(cr, uid, order, context=context))
        return invoice_vals

sale_order()

class account_invoice(osv.osv):
     _inherit = 'account.invoice'

     _columns = {
        'partner_partner_id': fields.many2one("res.partner.partner", 'Customer'),
        
     }
     
account_invoice()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
