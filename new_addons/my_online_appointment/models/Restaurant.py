from odoo import fields, models, api


class RestaurantName(models.Model):
    _name = 'restaurant.name'
    _description = 'Restaurant Name'

    name = fields.Char(string='Tên nhà hàng')
    address = fields.Char(string='Địa chỉ nhà hàng')
    email = fields.Char(string="Email")
    phone = fields.Char(unaccent=False)
    open = fields.Float(string="Thời gian mở cửa")
    close = fields.Float(string="Thời gian đóng cửa")
    facebook = fields.Char(string="Địa chỉ facebook")
    pinterest = fields.Char(string="Địa chỉ pinterest")
    twitter = fields.Char(string="Địa chỉ twiter")
