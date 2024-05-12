from odoo import fields, models, api


class Managertable(models.Model):
    _name = 'manager.table'
    _description = 'Manager table'

    name = fields.Char(string='Tên bàn ăn', required=True)
    capacity = fields.Many2one(comodel_name="capacity", string="Sức chứa của bàn")
    location_table = fields.Many2one(comodel_name="location.table", string="Vị trí của bàn ăn")
    characteristic = fields.Many2one(comodel_name="characteristic", string="Đặc điểm của bàn ăn")
    statu = fields.Boolean(string='Trạng thái', default=False, help="Đánh dấu bàn ăn có sẵn hoặc không")
    image_1920 = fields.Image(string='Avatar', max_width=1920, max_hieght=1920)
    image_128 = fields.Image("Image 128", related="image_1920", max_width=128, max_hieght=128, store=True)
    description = fields.Text(string="Mô tả bàn ăn")
    reservation_ids = fields.Many2many('reservation.time', string='Reservations')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id.id)
    price = fields.Monetary(string='Price', currency_field='currency_id')

    @api.model
    def create(self, vals):
        vals['statu'] = False  # Thiết lập trạng thái mặc định là "trống"
        return super(Managertable, self).create(vals)