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
{
    'name' : 'Deal Registration',
    'version' : '1.1',
    'author' : 'XXX',
    'category' : 'Products and Deals',
    'description' : """
Deal Protection.
    """,
    'website': 'http://www.openerp.com',
    'images' : [],
    'depends' : ['base', 'product', 'product_extended', 'base_action_rule', 'sale'],
    'data': [
        'deal_registration_view.xml',
        'deal_registration_sequence.xml',
        'deal_registration_workflow.xml',
        'deal_to_expire_reminder_demo.xml',
        'deal_reminder_template_data.xml',
    ],
    'js': [
    ],
    'qweb' : [
    ],
    'css':[
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
