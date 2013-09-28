# -*- coding: utf-8 -*-
##############################################################################
#
#    Account excal reports
#    Copyright (C) 2004-2010 BrowseInfo(<http://www.browseinfo.in>).
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
{
    'name': 'aeroo_report_accounts',
    'version': '0.1',
    'category': 'Tools',
    'description': """
This module update memos inside OpenERP for using an external pad
=================================================================
 this module is for aeroo reports of general ledger which one are is rml in openerp 7.0


""",
    'author': 'BrowseInfo',
    'website': 'www.browseinfo.in',
    'depends': [
        'account',
        'report_aeroo',
    ],
    'data': [
        'wizard/wizard_trail_balance_view.xml',
        'report/report_general_ledger_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
