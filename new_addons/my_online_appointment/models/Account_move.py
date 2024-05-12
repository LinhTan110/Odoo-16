from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    appointment_id = fields.Many2one('patient.appointment', string='Appointment')

    # restaurant_name = fields.Char(string="Restaurant name")
    address = fields.Char(string="Address")
    table = fields.Char(string='manager_table')
    capacity = fields.Integer(string='capacity')
    location_table = fields.Char(string='location_table')
    characteristic = fields.Char(string='characteristic')

    start = fields.Datetime(string='Ngày/giờ bắt đầu hẹn')
    stop = fields.Datetime(string='Ngày/giờ kết thúc hẹn')
    duration = fields.Float(string='Duration')
    allday = fields.Boolean('Cả ngày', default=False)
    start_date = fields.Date(string='Ngày bắt đầu hẹn')
    stop_date = fields.Date(string='Ngày kết thúc hẹn')

    phone = fields.Char(string='Phone', related='partner_id.phone')
    email = fields.Char(string='Email', related='partner_id.email')

    def get_restaurant_name(self):
        if self.appointment_id and self.appointment_id.restaurant_name:
            return self.appointment_id.restaurant_name.name
        return ''

    restaurant_name = fields.Char(string="Restaurant name", compute='compute_restaurant_name')

    @api.depends('appointment_id', 'appointment_id.restaurant_name')
    def compute_restaurant_name(self):
        for order in self:
            order.restaurant_name = order.get_restaurant_name()

    def print_restaurant_name(self):
        for sale_order in self:
            print(sale_order.get_restaurant_name())