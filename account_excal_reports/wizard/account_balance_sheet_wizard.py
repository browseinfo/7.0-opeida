from osv import osv, fields
from tools.translate import _

class account_balance_sheet_report(osv.osv_memory):
    """
    This wizard will provide the account balance sheet report by periods, between any two dates.
    """
    _inherit = 'accounting.report'
    _columns = {
              'currency_id' : fields.many2one('res.currency', 'Currency(1)', required=True),
              'currency_id_second' : fields.many2one('res.currency', 'Currency(2)', required=True),
               }
    
    def _print_report_excel(self, cr, uid, ids, data, context=None):
        data['form'].update(self.read(cr, uid, ids, ['date_from_cmp',  'debit_credit', 'date_to_cmp',  'fiscalyear_id_cmp', 'period_from_cmp', 'period_to_cmp',  'filter_cmp', 'account_report_id', 'enable_filter', 'label_filter'], context=context)[0])


        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account_balance_sheet_exel', 
                'datas': data
                 }

    
    def check_report_excel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['currency_id_second','currency_id','date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'period_from', 'period_to',  'filter',  'chart_account_id', 'target_move','debit_credit'], context=context)[0]
        
        
        for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
        data['form']['used_context'] = used_context
        data1 = {}
        data1['form'] = self.read(cr, uid, ids, ['currency_id_second','currency_id','account_report_id', 'date_from_cmp',  'date_to_cmp',  'fiscalyear_id_cmp', 'journal_ids', 'period_from_cmp', 'period_to_cmp',  'filter_cmp',  'chart_account_id', 'target_move'], context=context)[0]
        for field in ['fiscalyear_id_cmp', 'chart_account_id', 'period_from_cmp', 'period_to_cmp', 'account_report_id']:
            if isinstance(data1['form'][field], tuple):
                data1['form'][field] = data1['form'][field][0]
        comparison_context = self._build_comparison_context(cr, uid, ids, data1, context=context)
        data['form']['comparison_context'] = comparison_context
        return self._print_report_excel(cr, uid, ids, data, context=context)
    
account_balance_sheet_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
