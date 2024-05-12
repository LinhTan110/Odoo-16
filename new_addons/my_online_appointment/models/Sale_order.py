from datetime import timedelta

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    appointment_id = fields.Many2one('patient.appointment', string='Appointment')

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

    def action_view_appointment(self):
        if self.appointment_id:
            # Nếu có lịch hẹn liên kết, mở trực tiếp form view của lịch hẹn
            action = {
                'type': 'ir.actions.act_window',
                'name': 'Appointment',
                'view_mode': 'form',
                'res_model': 'patient.appointment',
                'res_id': self.appointment_id.id,
                'target': 'current',    #thay current bằng new để hiện form
                'context': self.env.context,
            }
            return action

    def get_restaurant_name(self):
        if self.appointment_id and self.appointment_id.restaurant_name:
            return self.appointment_id.restaurant_name.name
        return ''

    restaurant_name = fields.Char(string="Restaurant name", compute='compute_restaurant_name')

    @api.depends('appointment_id', 'appointment_id.restaurant_name')
    def compute_restaurant_name(self):
        for order in self:
            order.restaurant_name = order.get_restaurant_name()