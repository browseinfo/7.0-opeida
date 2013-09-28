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

from datetime import datetime, timedelta
import time
import openerp.addons.decimal_precision as dp
import openerp.exceptions

from openerp import netsvc
from openerp import pooler
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare

class deal_registration(osv.osv):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "deal.registration"
    _description = "Deals Registration"

    def action_approved(self, cr, uid, ids, context=None):
        context = context or {}
        for o in self.browse(cr, uid, ids):
            if not o.product_lines:
                raise osv.except_osv(_('Error!'),_('You cannot register a deal which has no line.'))
        return self.write(cr, uid, ids, {'state': 'approved'})

    def action_expired(self, cr, uid, ids, context=None):
        context = context or {}
        for o in self.browse(cr, uid, ids):
            if not o.product_lines:
                raise osv.except_osv(_('Error!'),_('You cannot register a deal which has no line.'))
        return self.write(cr, uid, ids, {'state': 'expired'})

    def _get_deal(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('product.product.lines').browse(cr, uid, ids, context=context):
            result[line.deal_id.id] = True
        return result.keys()

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for deal in self.browse(cr, uid, ids, context=context):
            res[deal.id] = {
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = deal.pricelist_id.currency_id
            for line in deal.product_lines:
                val1 += line.price_subtotal
            res[deal.id]['amount_total'] = cur_obj.round(cr, uid, cur, val1)
        return res

    _columns = {
        'name': fields.char('Description'),
        'user_id': fields.many2one('res.users', 'Responsible'),
        'company_id': fields.many2one('res.company', 'Company'),
        'partner_partner_id': fields.many2one('res.partner.partner', 'Customer'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', required=True, readonly=True, states={'new': [('readonly', False)]}, help="Pricelist for current Deal."),
        'date_deadline': fields.date('Deadline', required=True),
        'date_registration': fields.date('Deal Registration Date', readonly=True, required=True),
        'state': fields.selection([
            ('new','New'),
            ('approved','Approved'),
            ('closed','Closed'),
            ('expired','Expired'),
            ],'Status', readonly=True, track_visibility='onchange'),
        'product_lines': fields.one2many('product.product.lines', 'deal_id', string='Product Lines'),
        'active': fields.boolean('Active'),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'deal.registration': (lambda self, cr, uid, ids, c={}: ids, ['product_lines'], 10),
                'product.product.lines': (_get_deal, ['price_unit', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The total amount.", track_visibility='always'),
    }

    _defaults = {
        'name': lambda obj, cr, uid, context: '/',
        'date_deadline': fields.date.context_today,
        'date_registration': fields.date.context_today,
        'state': 'new',
        'active': True,
        'user_id': lambda self, cr, uid, context: uid,
    }

    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'deal.registration') or '/'
        return super(deal_registration, self).create(cr, uid, vals, context=context)

    def button_dummy(self, cr, uid, ids, context=None):
        return True

    def onchange_pricelist_id(self, cr, uid, ids, pricelist_id, product_lines, context=None):
        context = context or {}
        if not pricelist_id:
            return {}
        value = {
            'currency_id': self.pool.get('product.pricelist').browse(cr, uid, pricelist_id, context=context).currency_id.id
        }
        if not product_lines:
            return {'value': value}
        warning = {
            'title': _('Pricelist Warning!'),
            'message' : _('If you change the pricelist of this order (and eventually the currency), prices of existing order lines will not be updated.')
        }
        return {'warning': warning, 'value': value}

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        if not part:
            return {'value': {}}

        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
        dedicated_salesman = part.user_id and part.user_id.id or uid
        val = {
            'user_id': dedicated_salesman,
        }
        if pricelist:
            val['pricelist_id'] = pricelist
        val['partner_partner_id'] = part.partner_partner_id.id or False
        return {'value': val}

    def action_deal_reminder_send_mail(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the deal reminder template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'deal_registration', 'email_template_deal_registration')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(context)
        ctx.update({
            'default_model': 'deal.registration',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

deal_registration()

class product_product_lines(osv.osv):
    _name = "product.product.lines"

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
#        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
#            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id)
            cur = line.deal_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, price)
        return res

    _columns = {
        'deal_id': fields.many2one('deal.registration', 'Deal Reference', required=True, ondelete='cascade', select=True, readonly=True),
        'name': fields.text('Description', required=True),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of product lines."),
        'product_id': fields.many2one('product.product', 'Product', change_default=True),
        'product_uom_qty': fields.float('Quantity', digits_compute= dp.get_precision('Product UoS'), required=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure ', required=True),
        'product_uos_qty': fields.float('Quantity (UoS)' ,digits_compute= dp.get_precision('Product UoS')),
        'product_uos': fields.many2one('product.uom', 'Product UoS'),
        'order_partner_id': fields.related('deal_id', 'partner_id', type='many2one', relation='res.partner', store=True, string='Customer'),
        'salesman_id':fields.related('deal_id', 'user_id', type='many2one', relation='res.users', store=True, string='Responsible'),
        'company_id': fields.related('deal_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),
        
        'period_id': fields.related('product_id', 'period_id', type='many2one', relation='account.period', store=True, string='Period', readonly=True),
        'license': fields.related('product_id', 'license', type='char', relation='product.product', store=True, string='License', readonly=True),
        'expiry_date': fields.related('product_id', 'expiry_date', type='datetime', relation='product.product', store=True, string='Expiry Date', readonly=True),
        
        'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Product Price')),
        'type': fields.selection([('make_to_stock', 'from stock'), ('make_to_order', 'on order')], 'Procurement Method', required=True),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
        'address_allotment_id': fields.many2one('res.partner', 'Allotment Partner',help="A partner to whom the particular product needs to be allotted."),
        'discount': fields.float('Discount (%)', digits_compute= dp.get_precision('Discount')),
    }

    _order = 'deal_id desc, sequence, id'
    _defaults = {
        'discount': 0.0,
        'product_uom_qty': 1,
        'product_uos_qty': 1,
        'sequence': 10,
        'type': 'make_to_stock',
        'price_unit': 0.0,
    }

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, date_order=True, packaging=False, fiscal_position=False, flag=False, context=None):
        context = context or {}
        lang = lang or context.get('lang',False)
        warning = {}
        product_uom_obj = self.pool.get('product.uom')
        partner_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        context = {'lang': lang, 'partner_id': partner_id}
        if partner_id:
            lang = partner_obj.browse(cr, uid, partner_id).lang
        context_partner = {'lang': lang, 'partner_id': partner_id}

        if not product:
            return {'value': {'th_weight': 0,
                'product_uos_qty': qty}, 'domain': {'product_uom': [],
                   'product_uos': []}}
        if not date_order:
            date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

        result = {}
        warning_msgs = ''
        product_obj = product_obj.browse(cr, uid, product, context=context_partner)

        uom2 = False
        if uom:
            uom2 = product_uom_obj.browse(cr, uid, uom)
            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False
        if uos:
            if product_obj.uos_id:
                uos2 = product_uom_obj.browse(cr, uid, uos)
                if product_obj.uos_id.category_id.id != uos2.category_id.id:
                    uos = False
            else:
                uos = False
        fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False

        if not flag:
            result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
            if product_obj.description_sale:
                result['name'] += '\n'+product_obj.description_sale
        domain = {}
        if (not uom) and (not uos):
            result['product_uom'] = product_obj.uom_id.id
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
                uos_category_id = product_obj.uos_id.category_id.id
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
                uos_category_id = False
            result['th_weight'] = qty * product_obj.weight
            domain = {'product_uom':
                        [('category_id', '=', product_obj.uom_id.category_id.id)],
                        'product_uos':
                        [('category_id', '=', uos_category_id)]}
        elif uos and not uom: # only happens if uom is False
            result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
            result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
            result['th_weight'] = result['product_uom_qty'] * product_obj.weight
        elif uom: # whether uos is set or not
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
            result['th_weight'] = q * product_obj.weight        # Round the quantity up

        if not uom2:
            uom2 = product_obj.uom_id
        # get unit price

        if not pricelist:
            warn_msg = _('You have to select a pricelist or a customer in the deal registration form !\n'
                    'Please set one before choosing a product.')
            warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
        else:
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product, qty or 1.0, partner_id, {
                        'uom': uom or result.get('product_uom'),
                        'date': date_order,
                        })[pricelist]
            if price is False:
                warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
                        "You have to change either the product, the quantity or the pricelist.")

                warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
            else:
                result.update({'price_unit': price})
        if warning_msgs:
            warning = {
                       'title': _('Configuration Error!'),
                       'message' : warning_msgs
                    }
        result['period_id'] = product_obj.period_id.id or False
        result['license'] = product_obj.license or False
        result['expiry_date'] = product_obj.expiry_date or False
        return {'value': result, 'domain': domain, 'warning': warning}

    def product_uom_change(self, cursor, user, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, context=None):
        context = context or {}
        lang = lang or ('lang' in context and context['lang'])
        if not uom:
            return {'value': {'price_unit': 0.0, 'product_uom' : uom or False}}
        return self.product_id_change(cursor, user, ids, pricelist, product,
                qty=qty, uom=uom, qty_uos=qty_uos, uos=uos, name=name,
                partner_id=partner_id, lang=lang, date_order=date_order, context=context)

product_product_lines()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
