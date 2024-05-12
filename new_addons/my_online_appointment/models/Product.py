from odoo import fields, models, api
from odoo.tools import float_compare


class KeThuaProductTemplate(models.Model):
    _inherit = 'product.template'

    description = fields.Text(string="Mô tả món ăn")
    status = fields.Selection(string='Status', selection=[('còn', 'Còn'), ('hết', 'Hết')])
    time_preparation = fields.Float(string='Thời gian cần chuẩn bị')
    date_menu = fields.Date(string="Ngày món ăn vào menu")
    ingredients = fields.Many2many(comodel_name="ingredients.ingredients", string="Nguyên liệu nấu ăn")

    @api.model
    def get_dish_lists(self):
        dish_lists = self.env['dish.list'].search([])
        return dish_lists