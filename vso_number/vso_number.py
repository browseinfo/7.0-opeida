# -*- coding: utf-8 -*-
import datetime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp import tools
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc
import datetime
import csv


class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'
    _columns = {
        'name': fields.char('VSO Number', size=64, required=True),
#        'otc_ids': fields.many2many('otc.license', 'otc_license_lot_rel', 'vso_id', 'otc_id'),
        'otc_ids' : fields.one2many('otc.license', 'vso_id', 'OTC'),
        'csv_path' : fields.char('Path CSV', size=264),
        }

    _defaults = {
        'name': False,
    }
    _sql_constraints = [
        ('vso_uniq', 'unique(name, product_id)', 'You can not select vso which is already created!'),
    ]
    def import_csv(self, cr, uid, ids, context=None):
            obj_seq = self.pool.get('ir.sequence')
            license = self.pool.get('otc.license')
            product_browse = self.pool.get('stock.production.lot').browse(cr,uid,ids[0])
            product = product_browse.product_id.id
            vso_obj = self.pool.get('vso.vso')
            aa = self.browse(cr,uid,ids)[0]
            ot = license.browse(cr,uid,ids)[0]
            cur_vso = aa.name
            vso = aa.name[3:8]+':'
            cr.execute('select name from stock_production_lot where id=%s',([aa.id]))
            res = cr.fetchall()
            total_len = len(res)-2
            vsoname = res[total_len][0]
            today = time.strftime('%d%m%y')
            aa = self.browse(cr,uid,ids)[0]
            now = datetime.datetime.now()
            if aa.csv_path:
                try:
                    datafile = open(aa.csv_path, 'r')
                except:
                    raise osv.except_osv(_('Error!'), _('Wrong CSV Path.'))
            datareader = csv.reader(datafile, delimiter='\t')
            no_of_otc = product_browse.product_id.no_otc
            data = []
            count = 1 
            row_len = 1
#            seq = "0000%d" % (int(00001))            
            seq = 00001           
            count_otc = 1
            for row in datareader:
                if count == 1:
                    count = 0
                    continue
                #seq = obj_seq.next_by_code(cr, uid, 'otc.license', context=context)
                qr_code = ''
                
                if cur_vso == vsoname:
                    if count_otc == no_of_otc:
                        qr_code = str(vso) + str(today) + ':' + '0000' + str(seq)
                        seq = int(seq) + 1
                        count_otc = 1
                    else:
                        qr_code = str(vso) + str(today) + ':' + '0000' + str(seq)
                        count_otc = count_otc + 1
#                    qr_code = vso + today + ':' + seq
#                 else:
#                     qr_code = vso + today + ':' + str('000') + str(int(seq))
#                 
#                     seq = str(int(seq)+1)
#                     qr_code = vso + today + ':' + str('00') + str(int(seq))
#                     seq = str(int(seq)+1)
                        
                data_create = {'otc':row[0],'vso_id':ids[0],
                               'runtime' : row[4], 'product_id': aa.product_id.id or '', 'activation_start_date' : row[1], 'activation_end_date' : row[2], 'expiry_date' : row[3], 'qr_no':qr_code}
                row_len = row_len + 1
                license.create(cr, uid,data_create,context=context)

stock_production_lot()

class purchase_order_line(osv.osv):
    _inherit='purchase.order.line'
    _columns = {
         'vso_id':fields.many2one('stock.production.lot','VSO Number',  select=True, domain="[('product_id','=',product_id)]"),
    }

purchase_order_line()

class purchase_order(osv.osv):
    _inherit='purchase.order'
    _columns = {
         'vso_id':fields.many2one('stock.production.lot','VSO Number',  select=True, domain="[('product_id','=',product_id)]"),
    }
    
    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
        res = super(purchase_order, self)._prepare_order_line_move(cr, uid, order, order_line, picking_id, context=context)
        res.update({'prodlot_id': order_line.vso_id.id})
        return res
  
purchase_order()

class sale_order_line(osv.osv):
    _inherit='sale.order.line'
    _columns = {
        'box_id':fields.many2one('box.box','Boxes'),
        'vso_line_ids': fields.one2many('vso.vso', 'order_line_id', 'VSO Order Lines'),
	'with_box': fields.boolean('With Box'),
    }

#    def write(self, cr, uid, ids, vals, context=None):
#        res=super(sale_order_line, self).write(cr, uid, ids, vals, context=context)
#        box_obj = self.pool.get('box.box')
#        vso_obj = self.pool.get('stock.production.lot')
#        sol = self.browse(cr, uid, ids, context=context)[0]
#        order = sol.order_id
#        prod_ids = self.pool.get('product.product').search(cr, uid, [('description','=','Box'),('type','=','product'),#('procure_method','=','make_to_order'),('supply_method','=','buy')], context=context)
#        for p in self.pool.get('product.product').browse(cr, uid, prod_ids):
#            if p.name == 'Box':
#                box=p.id
#        if vals.get('vso_id'):
#            vso=vals.get('vso_id')
#            vso = self.pool.get('stock.production.lot').browse(cr, uid, vso, context=context)
#            qr=self.browse(cr, uid, ids, context=context)[0].qr_no
#            if vso.name and qr:
#                qr_rec=qr.split(':')
#                if len(qr_rec)==3:
#                    qr_rec[0]=vso.name[0:5]
#                    new_qr=qr_rec[0]+':'+qr_rec[1]+':'+qr_rec[2]
#                else:
#                    new_qr=vso.name+':'+qr
#                vals.update({'qr_no':new_qr})
#        if vals.get('package_type') and vals.get('package_type') == 'box':
#            for x in order.order_line:
#                if x.product_id.id == box:
#                    box_qty = x.product_uom_qty
#                    vals.update({'product_uom_qty':box_qty+1})
#                    return res and super(sale_order_line, self).write(cr, uid, [x.id], vals, context=context)
#        return res

    def create(self, cr, uid, vals, context=None):
        vso_obj = self.pool.get('vso.vso')
        qty = 0.0
        vso_lines = vals.get('vso_line_ids')
        if vso_lines:
            for vso in vso_lines:
                if vso and vso[2]:
                    qty += vso[2].get('product_qty')  
            if qty > vso[2].get('product_qty'):
                raise osv.except_osv(_('Warning!'),
                                             _('Vso line Quantity "%s" is greater then total selected vso quantity "%s"."') % (qty, vso[2].get('product_qty')))
        return super(sale_order_line, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        res = super(sale_order_line, self).write(cr, uid, ids, vals, context=context)
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        lines = []
        product_obj = self.pool.get('product.product')
        pro = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'vso_number', 'product_product_box')[1]
        reco = product_obj.browse(cr, uid, pro, context=context)
        if vals.get('product_id') or vals.get('product_uom_qty'):
            if not vals.get('product_id'):
                prod_id = self.browse(cr, uid, ids[0], context=context).product_id
                no_otc = prod_id.no_otc
            else:
                no_otc = product_obj.browse(cr, uid, vals.get('product_id'), context=context).no_otc or 0.0
            old_line = self.browse(cr, uid, ids[0], context=context) 
            is_box = old_line.with_box
            old_line_qty = old_line.product_uom_qty 
            if old_line.product_id.no_otc != 0:
#                 raise osv.except_osv(_('Warning!'),
#                                              _('Invalid OTC!'))
                old_line_box_qty = old_line_qty/old_line.product_id.no_otc 
                qty = vals.get('product_uom_qty') or 0.0
                order_id = self.browse(cr, uid, ids[0]).order_id.id

            if is_box:
                new_line_box_qty = qty / no_otc
                update_box_id = self.search(cr, uid, [('order_id', '=', order_id),('product_id', '=', pro)], context=context)
                line_browse = self.browse(cr, uid, update_box_id)[0]
                old_box_qty = line_browse.product_uom_qty
                box_qty = old_box_qty - old_line_box_qty + new_line_box_qty
                line_browse.write({'product_uom_qty': box_qty})
                return res
            else:
                return res

sale_order_line()

class sale_order(osv.osv):

    _inherit = "sale.order"
    _columns = {
        'vso_id':fields.many2one('stock.production.lot','VSO Number', select=True, domain="[('product_id','=',product_id)]"),
    }

    def create(self, cr, uid, vals, context=None):
        res = super(sale_order, self).create(cr, uid, vals, context=context)
        sale_line = self.pool.get('sale.order.line')
        vso_obj = self.pool.get('vso.vso')
        qty = 0.0
        boxqty = 0.0
        vso_lines = vals.get('vso_line_ids')
        product_obj = self.pool.get('product.product')
        line = vals.get('order_line')
        lines = len(line)
        product_qty = line[0][2]['product_uom_qty']
        product = line[0][2]['product_id']
        box = line[0][2]['with_box']
        otc = product_obj.browse(cr, uid, product, context=context).no_otc or 0
        pro = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'vso_number', 'product_product_box')[1]
        reco = product_obj.browse(cr, uid, pro, context=context)
        if otc == 0:
                raise osv.except_osv(_('Warning!'),
                                             _('Invalid OTC!'))
        i = 0 
        test = 0       
        while(i < lines):
            test += line[i][2]['product_uom_qty'] / otc
            i +=1
        if box == True:
            boxqty = product_qty / otc
            vals = {'product_uom_qty' : test,'price_unit':1,'name':reco.name,'product_id': pro, 'uom_id':reco.uom_id,
                    'order_id':res}
            sale_line.create(cr, uid, vals)

        if vso_lines:
            for vso in vso_lines:
                if vso and vso[2]:
                    qty += vso[2].get('product_qty')                    
            if qty > vso_qty:
                raise osv.except_osv(_('Warning!'),
                                             _('Vso line Quantity "%s" is greater then total selected vso quantity "%s"."') % (qty, vso_qty))
        return res

    def _prepare_vso_order_line_move(self, cr, uid, order, line, vso, picking_id, date_planned, context=None):
        location_id = order.shop_id.warehouse_id.lot_stock_id.id
        output_id = order.shop_id.warehouse_id.lot_output_id.id
        return {
            'name': line.name,
            'picking_id': picking_id,
            'product_id': line.product_id.id,
            'date': date_planned,
            'date_expected': date_planned,
            'product_qty': vso.product_qty,
            'product_uom': line.product_uom.id,
            'product_uos_qty': vso.product_qty,
            'product_uos': (line.product_uos and line.product_uos.id)\
                    or line.product_uom.id,
            'product_packaging': line.product_packaging.id,
            'partner_id': line.address_allotment_id.id or order.partner_shipping_id.id,
            'location_id': location_id,
            'location_dest_id': output_id,
            'sale_line_id': line.id,
            'tracking_id': False,
            'prodlot_id': vso.vso_id and vso.vso_id.id or False,
            'state': 'draft',
            #'state': 'waiting',
            'company_id': order.company_id.id,
            'price_unit': line.product_id.standard_price or 0.0
        }

    def _create_pickings_and_procurements(self, cr, uid, order, order_lines, picking_id=False, context=None):
        """Create the required procurements to supply sales order lines, also connecting
        the procurements to appropriate stock moves in order to bring the goods to the
        sales order's requested location.

        If ``picking_id`` is provided, the stock moves will be added to it, otherwise
        a standard outgoing picking will be created to wrap the stock moves, as returned
        by :meth:`~._prepare_order_picking`.

        Modules that wish to customize the procurements or partition the stock moves over
        multiple stock pickings may override this method and call ``super()`` with
        different subsets of ``order_lines`` and/or preset ``picking_id`` values.

        :param browse_record order: sales order to which the order lines belong
        :param list(browse_record) order_lines: sales order line records to procure
        :param int picking_id: optional ID of a stock picking to which the created stock moves
                               will be added. A new picking will be created if ommitted.
        :return: True
        """
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        procurement_obj = self.pool.get('procurement.order')
        proc_ids = []

        for line in order_lines:
            if line.state == 'done':
                continue

            date_planned = self._get_date_planned(cr, uid, order, line, order.date_order, context=context)

            if line.product_id:
                if line.product_id.type in ('product', 'consu'):
                    vso = False
                    total_vso_qty = 0.00
                    if not picking_id:
                        picking_id = picking_obj.create(cr, uid, self._prepare_order_picking(cr, uid, order, context=context))
                    if line.vso_line_ids:
                        for vso in line.vso_line_ids:
                            if vso.vso_id.product_id != line.product_id:
                                raise osv.except_osv(_('Warring!'),
                                                     _('Order line product "%s" is not same vso line product "%s".  Please select same product vso number"') % (line.product_id.name, vso.vso_id.product_id.name))
                            total_vso_qty += vso.product_qty
                        if total_vso_qty > line.product_uom_qty:
                            raise osv.except_osv(_('Warning!'),
                                                 _('Vso line Quantity "%s" is greater then total selected vso quantity "%s"."') % (total_vso_qty, line.product_uom_qty))

                        move_id = move_obj.create(cr, uid, self._prepare_vso_order_line_move(cr, uid, order, line, vso, picking_id, date_planned, context=context))
                    else:
                        move_id = move_obj.create(cr, uid, self._prepare_order_line_move(cr, uid, order, line, picking_id, date_planned, context=context))
                else:
                    # a service has no stock move
                    move_id = False

                proc_id = procurement_obj.create(cr, uid, self._prepare_order_line_procurement(cr, uid, order, line, move_id, date_planned, context=context))
                proc_ids.append(proc_id)
                line.write({'procurement_id': proc_id})
                self.ship_recreate(cr, uid, order, line, move_id, proc_id)

        wf_service = netsvc.LocalService("workflow")
        if picking_id:
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        for proc_id in proc_ids:
            wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)

        val = {}
        if order.state == 'shipping_except':
            val['state'] = 'progress'
            val['shipped'] = False

            if (order.order_policy == 'manual'):
                for line in order.order_line:
                    if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
                        val['state'] = 'manual'
                        break
        order.write(val)
        return True


sale_order() 

class box(osv.osv):
    _name = 'box.box'
    _columns = {
        'name': fields.float('QR Number'),
        'product_id': fields.many2one('product.product', 'Product'),
    }
box()

class vso_vso(osv.osv):
    _name = 'vso.vso'
    _columns = {
        'vso_id':fields.many2one('stock.production.lot','VSO Number', select=True, required=True),
        'product_qty': fields.float('Quantity', digits_compute= dp.get_precision('Product UoS'), required=True),
        'order_line_id': fields.many2one('sale.order.line', 'order'),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'otc_ids': fields.many2many('otc.license', id1='vso_vso_id', id2='otc_id',string='OTC'),
    }
    def onchange_quantity(self, cr, uid, ids, vso_id, product_id, product_qty, context=None):     
        lot_obj_browse = self.pool.get('stock.production.lot').browse(cr, uid, vso_id)
	product_obj_browse = self.pool.get('product.product').browse(cr, uid, product_id)
	print "\n\nProduct", product_obj_browse, product_obj_browse.no_otc
	if product_obj_browse.no_otc <= 0:
		raise osv.except_osv(_('Warning!'),
        		_('Enter Vaild OTC'))
	
        if product_qty > lot_obj_browse.stock_available:
        	raise osv.except_osv(_('Warning!'),
			_('Vso line Quantity "%s" is greater then vso available quantity "%s" .  Please  do not select more then vso available quantity"') % (product_qty, lot_obj_browse.stock_available))
	
        if vso_id:
            otc = self.pool.get('otc.license').search(cr, uid, [('vso_id','=', vso_id), ('sold', '=', False)], limit=(product_qty * product_obj_browse.no_otc), context=context)
            result = {
                    'otc_ids': [(6,0,[x_id for x_id in otc])]
                    }
        return {'value': result}                                                     
    
'''    def onchange_vso_id(self, cr, uid, ids, vso_id=False,product_qty=0.0, context=None):
        if not vso_id:
            return {}
        if vso_id:
            print "$$$$$$$$$$$$$$$$$$$$", product_qty
            otc = self.pool.get('otc.license').search(cr, uid, [('vso_id','=', vso_id), ('sold', '=', False)], context=context)
            result = {
                    'otc_ids': [(6,0,[x_id for x_id in otc])]
                    }
        return {'value': result}'''
vso_vso()
