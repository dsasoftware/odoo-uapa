#-*- coding: utf-8 -*-
#####
#
#Localization for payroll to the Dominican Republic.
#Modifications to the hr.payslip.run object.
#
#Author: José Ernesto Mendez @ Open Business Solutions
#
#
#####

from openerp.osv import orm, fields, osv

class hr_payslip_run (orm.Model) :

    _name = 'hr.payslip.run'
    _inherit = 'hr.payslip.run'
    _columns = {
        'date_efective': fields.date('Fecha de Aplicacion', required=True,
            readonly=True, states={'draft':[('readonly', False)]}, select=True,
            help="""Date when the payment is applied. - The application date
            can't be lower than the date when the text file was sent to the
            bank."""),
        'company_id': fields.many2one('res.company', 'Empresa', required=True,
            readonly=True, states={'draft':[('readonly',False)]}),
        'currency_id': fields.many2one('res.currency', 'Moneda',
            required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'bank_id': fields.many2one('res.bank', 'Banco', required=True,
            readonly=True, states={'draft':[('readonly',False)]}),
        'sequence': fields.char('Sequencia Lote Nomina', size=7,
            required=False, readonly=True, select=True, help="""Unique number
            of the payslip batch,computed automatically when the payslip batch
            is created."""),
    }

    def _get_seq(self, cr, uid, ctx):

        seq = self.pool.get('ir.sequence').get(cr, uid, 'salary.slipbatch')
        return seq

    def _get_currency(self, cr, uid, ctx):

        comp = self.pool.get('res.users').browse(cr, uid, uid).company_id
        if not comp:
            comp_id = self.pool.get('res.company').search(cr, uid, [])[0]
            comp = self.pool.get('res.company').browse(cr, uid, comp_id)
        return comp.currency_id.id

    def close_payslip_run(self, cr, uid, ids, context=None):
        slip_pool = self.pool.get('hr.payslip')
        slip_ids = [x.id for x in self.browse(cr, uid,ids[0], context=context).slip_ids]
        slip_pool.process_sheet(cr, uid, slip_ids, context=context)
        return self.write(cr, uid, ids, {'state': 'close'}, context=context)

    def confirm_payslips(self, cr, uid, ids, context=None):
        for payslip_run in self.browse(cr, uid, ids, context=context):
            payslip_obj = self.pool.get('hr.payslip')
            payslips = payslip_obj.browse(cr, uid, payslip_run.slip_ids, context)
            for payslip in payslips:
                payslip_id = payslip.id
                payslip_id.process_sheet()

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.payslip.run', context=c),
        'currency_id': _get_currency,
        'sequence': _get_seq,
    }

hr_payslip_run()
