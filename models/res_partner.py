from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    order_ids = fields.One2many('sale.order', 'partner_id', string='Sale Orders')
    unpaid_sale_order_ids = fields.One2many('sale.order', compute='_compute_unpaid_sale_orders')
    unpaid_sale_order_count = fields.Integer(compute='_compute_unpaid_sale_orders')

    total_sale_amount = fields.Float(string='Total Sale Amount', compute='_compute_total_sale_amount')
    commission_amount = fields.Float(string='Commission Amount', compute='_compute_commission_amount')
    unpaid_commission_amount = fields.Float(string='Unpaid Commission Amount', compute='_compute_unpaid_commission_amount')
    commission_ids = fields.One2many('commission.commission', 'partner_id', string='Commissions')
    partner_id = fields.Many2one('res.partner', string='Partner')

    @api.depends('order_ids')
    def _compute_unpaid_sale_orders(self):
        for partner in self:
            unpaid_orders = partner.order_ids.filtered(lambda o: not o.invoice_ids)
            partner.unpaid_sale_order_ids = unpaid_orders
            partner.unpaid_sale_order_count = len(unpaid_orders)

    @api.depends('order_ids.amount_total')
    def _compute_total_sale_amount(self):
        for partner in self:
            partner.total_sale_amount = sum(order.amount_total for order in partner.order_ids)

    @api.depends('commission_ids.amount_total')
    def _compute_commission_amount(self):
        for partner in self:
            partner.commission_amount = sum(commission.amount_total for commission in partner.commission_ids)

    @api.depends('commission_ids.amount_total', 'commission_ids.state')
    def _compute_unpaid_commission_amount(self):
        for partner in self:
            unpaid_commissions = partner.commission_ids.filtered(lambda c: c.state != 'paid')
            partner.unpaid_commission_amount = sum(commission.amount_total for commission in unpaid_commissions)

    def action_pay_commission(self):
        for partner in self:
            unpaid_commissions = partner.commission_ids.filtered(lambda c: c.state != 'paid')
            unpaid_commissions.action_pay_commission()
        return True

    def action_create_commission(self):
        for partner in self:
            if partner.unpaid_sale_order_count:
                commission = self.env['commission.commission'].create({
                    'partner_id': partner.id,
                    'order_id': partner.unpaid_sale_order_ids[0].id,
                })
                commission.onchange_commission_percentage()
                commission.action_pay_commission()
        return True