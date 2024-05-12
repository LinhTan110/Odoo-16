from odoo import fields, models, api


class RestaurantPolicy(models.Model):
    _name = 'restaurant.policy'
    _description = 'Restaurant Policy'

    name = fields.Char(string='Tên chính sách')
    description = fields.Text(string="Mô tả chính sách")
