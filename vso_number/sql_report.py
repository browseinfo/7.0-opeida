# -*- coding: utf-8 -*-

from openerp.osv import fields,osv
from openerp import tools
 
class otc_report_model(osv.osv):
    _name = "otc.report.model"
    _description = "Otc Report"
    _auto = False
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Customer', readonly=True),
        'name': fields.char('SO', size=128, readonly=True),
        'vso': fields.char('VSO', readonly=True),
        'otc': fields.char('OTC', readonly=True),
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        'expiry_date': fields.date('Expiry Date', readonly=True),
        'activation_start_date': fields.date('Activation Date', readonly=True),
        
    }

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'otc_report_model')
        cr.execute("""
            CREATE OR REPLACE VIEW otc_report_model AS(
            SELECT s.partner_id AS id,
                o.otc,
                s.name, 
                v.product_id,
                l.name as vso,
                o.expiry_date,
                o.activation_start_date,
                s.partner_id
            FROM 
                vso_vso v,stock_production_lot l,otc_license o, sale_order s
            WHERE s.id = o.vso_id
            GROUP BY s.partner_id,o.otc,s.name,l.name,o.expiry_date,o.activation_start_date,v.product_id
            )
        """)
 
otc_report_model()