# -*- coding: utf-8 -*-
##############################################################################
#
#    Sales and Account Invoice Discount Management
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
    'name': 'Project task history',
    'version': '0.2',
    'author': 'BrowseInfo',
    'website': 'http://www.browseinfo.in',
    'category': 'Tools',
    'installable': True,
    'auto_install': False,
    'data': [
        'project_task_imp_view.xml'
    ],
    'depends': ['project'],
    'description': """
Module to add history tab in project model.
================================================
"""
}
