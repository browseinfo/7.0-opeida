
# -*- coding: utf-8 -*-
# Browse Info
{
    'name': 'VSO Number',
    'version': '1.1',
    'author': 'Browse Info',
    'category': 'stock',
    'sequence': 21,
    'website': 'http://www.openerp.com',
    'summary': 'VSO Number',
    'description': """ 
        Uset for the Stock   
      """,
    'images': [   ],
    'depends': ['sale_mrp', 'otc_license'],
    'data': [
        'product_data.xml',
        'vso_sequence.xml',
        'vso_number_view.xml',
    ],
    'css' : ['static/src/css/vso.css'],
    'demo': [],
    'test': [ ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
