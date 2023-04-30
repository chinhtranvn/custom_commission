from odoo import api, fields, models


class Commission(models.Model):
    _name = 'commission.commission'
    _description = 'Commission'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    order_id = fields.Many2one('sale.order', string='Order', required=True,
                               domain="[('partner_id', '=', partner_id)]")
    currency_id = fields.Many2one(related='order_id.currency_id', string='Currency', readonly=True)
    amount_total = fields.Monetary(related='order_id.amount_total', string='Total Amount', readonly=True, currency_field='currency_id')
    commission_percentage = fields.Float(string='Commission Percentage')
    commission_amount = fields.Monetary(string='Commission Amount', readonly=True)
    payment_date = fields.Date(string='Payment Date')
    state = fields.Selection([('draft', 'Draft'), ('paid', 'Paid')], default='draft')

    @api.onchange('commission_percentage', 'amount_total')
    def onchange_commission_percentage(self):
        if self.commission_percentage:
            self.commission_amount = self.amount_total * self.commission_percentage / 100

    def action_pay_commission(self):
        if not self.commission_percentage:
            raise UserError('Please enter a commission percentage')
        if self.commission_amount <= 0:
            raise UserError('Commission amount must be greater than zero')
        account_move = self.env['account.move'].create({
            'ref': f'Commission {self.id}',
            'type': 'entry',
            'journal_id': self.env.ref('account_custom.journal_commission').id,
            'line_ids': [
                (0, 0, {
                    'name': f'Commission for {self.partner_id.name}',
                    'debit': self.commission_amount,
                    'account_id': self.env.ref('account_custom.account_commission_receivable').id,
                }),
                (0, 0, {
                    'name': f'Commission for {self.partner_id.name}',
                    'credit': self.commission_amount,
                    'account_id': self.env.ref('account_custom.account_commission_income').id,
                }),
            ],
        })
        account_move.action_post()
        self.write({'state': 'paid'})
        self.order_id.write({'commission_paid': True})
