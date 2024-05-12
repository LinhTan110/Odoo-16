from odoo import fields, models, api, _
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError


class KeThuaAppointment(models.Model):
    _inherit = 'patient.appointment'
    _description = 'Ke Thua Appointment'

    hospital = fields.Many2one(comodel_name="confi.hospital", string="Hospital")
    blood_id = fields.Many2one(comodel_name="blood.group", string='Blood Group')
    dieases = fields.Many2one(comodel_name="dieases.dieases", string="Dieases/Reason")
    dr_nm = fields.Many2one(comodel_name='doctor.config', string="Doctor")

    email = fields.Char(string="Email")
    phone = fields.Char(unaccent=False)
    note = fields.Text(string="Ghi chú")
    capacity = fields.Many2one(comodel_name="capacity", string="Sức chứa của bàn")
    location_table = fields.Many2one(comodel_name="location.table", string="Vị trí của bàn ăn")
    characteristic = fields.Many2one(comodel_name="characteristic", string="Đặc điểm của bàn ăn")
    show_empty_tables = fields.Boolean(string='Hiển thị tất cả bàn ăn', default=False)

    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id)

    price = fields.Monetary(string='Price', currency_field='currency_id', compute='compute_table_price', store=True)
    address = fields.Char(string='Địa chỉ nhà hàng', compute="_compute_address")
    product_ids = fields.Many2many('product.product', required=False)

    partner_id = fields.Many2one('res.partner', string='Customer', compute='_compute_customer_id', store=True)

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=True, inverse_name='appointment_id')
    allday = fields.Boolean('All Day', default=False)
    start_date = fields.Date(string='Start Date', store=True, tracking=True, compute='_compute_dates')
    stop_date = fields.Date(string='End Date', store=True, tracking=True, compute='_compute_dates')
    duration = fields.Float('Duration', compute='_compute_duration', store=True, readonly=False)
    start = fields.Datetime(string='Start', required=True, tracking=True, default=fields.Date.today,
                            help="Start date of an event, without time for full days events")
    stop = fields.Datetime(string='Stop', required=True, tracking=True,
                           default=lambda self: fields.Datetime.today() + timedelta(hours=1), compute='_compute_stop',
                           readonly=False, store=True, help="Stop date of an event, without time for full days events")
    state = fields.Selection(selection=[('draft', "Unconfirmed"), ('sale', "Confirmed"), ('cancel', "Cancelled")],
                             string="Status", readonly=True, copy=False, index=True, tracking=3, default='draft')
    matching_tables = fields.Many2many(comodel_name='manager.table', string='Matching Tables',
                                       compute='_compute_matching_tables')
    manager_table = fields.Many2one(comodel_name="manager.table", string="Bàn ăn",
                                    domain="[('id', 'in', matching_tables)]")
    search_button = fields.Boolean(string='Search table', default=True)
    refresh_button = fields.Boolean(string="Refresh Tables")
    reservation_id = fields.Many2one('reservation.time', string='Reservation Record', ondelete='set null')

    @api.model
    def _default_restaurant_name(self):
        default_restaurant = self.env['restaurant.name'].search([], limit=1)
        return default_restaurant.id if default_restaurant else False

    restaurant_name = fields.Many2one(comodel_name='restaurant.name', string='Tên nhà hàng',
                                      default=_default_restaurant_name)

    def open_reservation(self):
        self.ensure_one()  # Đảm bảo chỉ gọi method này trên một bản ghi tại một thời điểm
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Reservation',
            'view_mode': 'form',
            'res_model': 'reservation.time',
            'res_id': self.reservation_id.id,  # ID của bản ghi reservation.time liên kết
            'target': 'new',
            'context': self.env.context,
        }
        return action

    @api.model
    def create(self, vals):
        if ('start' in vals and 'stop' in vals and 'manager_table' in vals and 'capacity' in vals
                and 'location_table' in vals and 'characteristic' in vals):
            start_datetime = fields.Datetime.from_string(vals['start'])
            stop_datetime = fields.Datetime.from_string(vals['stop'])
            manager_table_id = vals['manager_table']
            capacity_id = vals['capacity']
            location_table_id = vals['location_table']
            characteristic_id = vals['characteristic']

            reservation_vals = {
                'table_id': manager_table_id,
                'capacity': capacity_id,
                'location_table': location_table_id,
                'characteristic': characteristic_id,
            }
            if vals.get('allday'):
                reservation_vals.update({
                    'start': vals.get('start'),
                    'stop': vals.get('stop'),
                    'allday': True,
                })
            else:
                reservation_vals.update({
                    'start_date': start_datetime.date(),
                    'stop_date': stop_datetime.date(),
                    'start': vals.get('start'),  # Cập nhật trường start ở đây
                    'stop': vals.get('stop'),
                    'duration': self._get_duration(start_datetime, stop_datetime),
                })
            reservation_record = self.env['reservation.time'].create(reservation_vals)
            vals['reservation_id'] = reservation_record.id
        self.create_customer(vals)
        return super(KeThuaAppointment, self).create(vals)

    def write(self, vals):
        res = super(KeThuaAppointment, self).write(vals)    # Cập nhật thông tin của KeThuaAppointment
        for record in self:     # Xử lý liên kết và cập nhật reservation.time
            if record.reservation_id:
                reservation_vals = {}   # Chuẩn bị dữ liệu cập nhật cho reservation.time
                field_map = {
                    'manager_table': 'table_id',
                    'capacity': 'capacity',
                    'location_table': 'location_table',
                    'characteristic': 'characteristic',
                    'start': 'start',
                    'stop': 'stop',
                    'start_date': 'start_date',
                    'stop_date': 'stop_date',
                    'duration': 'duration',
                    'allday': 'allday'
                }
                for kethua_field, reservation_field in field_map.items():   # Duyệt qua các trường và cập nhật giá trị nếu chúng có trong `vals`
                    if kethua_field in vals:
                        reservation_vals[reservation_field] = vals[kethua_field]
                if reservation_vals:    # Cập nhật dữ liệu cho reservation.time nếu có sự thay đổi
                    record.reservation_id.write(reservation_vals)
        return res

    @api.depends('capacity', 'location_table', 'characteristic', 'show_empty_tables', 'search_button', 'refresh_button')
    def _compute_matching_tables(self):
        for record in self:
            domain = [
                ('capacity', '=', record.capacity.id),
                ('location_table', '=', record.location_table.id),
                ('characteristic', '=', record.characteristic.id)
            ]
            if not record.show_empty_tables:
                domain.append(('statu', '=', False))
            else:
                domain.append('|')
                domain.append(('statu', '=', True))  # Lọc bàn có trạng thái 'Bận'
                domain.append(('statu', '=', False))  # Chỉ hiển thị bàn có trạng thái 'Trống'
            if record.search_button or record.refresh_button:  # Nếu nút "Tìm kiếm bàn" được nhấn, thực hiện tìm kiếm và ẩn bàn đã đặt trùng thời gian
                existing_reservations = self.env['reservation.time'].search([
                    ('start', '<', record.stop),
                    ('stop', '>', record.start)
                ])
                booked_tables_ids = existing_reservations.mapped('table_id.id')
                domain.append(('id', 'not in', booked_tables_ids))

            matching_tables = self.env['manager.table'].search(domain)
            record.matching_tables = matching_tables.ids

    @api.model
    def create_customer(self, vals):
        existing_customer = self.env['res.partner'].search([
            ('name', '=', vals['name']),
            ('email', '=', vals['email']),
            ('phone', '=', vals['phone'])
        ], limit=1)
        if existing_customer:  # Nếu khách hàng đã tồn tại với email đã cho, không tạo mới
            vals['partner_id'] = existing_customer.id
        else:
            customer_vals = {  # Tạo mới khách hàng với các giá trị từ vals
                'name': vals['name'],
                'email': vals['email'],
                'phone': vals['phone'],
                # Thêm các trường khách hàng khác bạn muốn tạo ở đây
            }
            new_customer = self.env['res.partner'].create(customer_vals)
            vals['partner_id'] = new_customer.id

    def unlink(self):
        for rec in self:
            if rec.reservation_id:
                rec.reservation_id.unlink()
        return super(KeThuaAppointment, self).unlink()

    def create_order_selection(self):
        for rec in self:
            rec.action_create_sale_order()

    def button_refresh_tables(self):
        self.ensure_one()
        self.manager_table = False
        self._compute_matching_tables()

    def action_create_sale_order(self):
        sale_order = None
        SaleOrder = self.env['sale.order'].sudo()
        for appointment in self:
            if appointment.state != 'sale':
                raise UserError(_("You can only create a sale order for confirmed appointments."))

            existing_sale_order = SaleOrder.search([('appointment_id', '=', appointment.id)],
                                                                limit=1)  # Kiểm tra xem đã có hóa đơn từ lịch hẹn này chưa
            duration = appointment.duration or 0.0  # Trích xuất giá trị duration từ appointment hoặc set mặc định nếu không có

            line_vals = []
            for product in appointment.product_ids:
                line_vals.append({
                    'order_id': existing_sale_order.id,
                    'product_id': product.id,
                    'name': product.name,
                })
            vals = {
                'partner_id': appointment.partner_id.id,
                'table': appointment.manager_table.name,
                'capacity': appointment.capacity.id,
                'location_table': appointment.location_table.name,
                'characteristic': appointment.characteristic.name,
                'start': appointment.start,
                'stop': appointment.stop,
                'start_date': appointment.start_date,
                'stop_date': appointment.stop_date,
                'allday': appointment.allday,
                'duration': duration,
                'restaurant_name': appointment.restaurant_name,
                'address': appointment.address,
                'order_line': [(0,0,v) for v in line_vals]
            }
            if existing_sale_order:  # Kiểm tra xem đơn hàng đã bị hủy hay không
                if existing_sale_order.state == 'cancel':  # Nếu đơn hàng đã bị hủy, tạo một đơn hàng mới
                    vals.update({'appointment_id': appointment.id})
                    sale_order = SaleOrder.create(vals)
                    appointment.sale_order_id = sale_order.id  # Gán ID của hóa đơn cho lịch hẹn
                else:
                    if appointment.product_ids:  # Cập nhật lại các dòng sản phẩm trong hóa đơn
                        existing_sale_order.order_line.unlink()  # Xóa các dòng sản phẩm cũ
                    existing_sale_order.write(vals)  # Nếu đơn hàng không bị hủy, cập nhật lại thông tin)
                    sale_order = existing_sale_order
            else:
                vals.update({'appointment_id': appointment.id})
                sale_order = SaleOrder.create(vals)# Nếu chưa có hóa đơn, tạo mới
                appointment.sale_order_id = sale_order.id  # Gán ID của hóa đơn cho lịch hẹn

        return {
            'name': _('Sale Order Information'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': sale_order.id if sale_order else False,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def action_view_sale_orders(self):
        if self.sale_order_id:
            action = {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'sale.order',
                'res_id': self.sale_order_id.id,
                'target': 'current',
            }
        else:
            action = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Sale Order Found'),
                    'message': _('No sale order has been created for this appointment.'),
                    'sticky': False,
                }
            }
        return action

    @api.depends('restaurant_name.address')
    def _compute_address(self):
        for record in self:
            if record.restaurant_name and record.restaurant_name.address:
                record.address = record.restaurant_name.address
            else:
                record.address = ''

    @api.depends('manager_table')
    def compute_table_price(self):
        for record in self:
            if record.manager_table:
                record.price = record.manager_table.price
            else:
                record.price = 0.0

    @api.depends('name', 'email', 'phone')
    def _compute_customer_id(self):
        for appointment in self:
            customer = self.env['res.partner'].search([
                ('name', '=', appointment.name),
                ('email', '=', appointment.email),
                ('phone', '=', appointment.phone)
            ], limit=1)
            appointment.partner_id = customer

    def action_view_customer(self):
        customer = self.env['res.partner'].search([  # Tìm khách hàng có cùng thông tin (name, email, phone)
            ('name', '=', self.name),
            ('email', '=', self.email),
            ('phone', '=', self.phone)
        ], limit=1)

        if customer:  # Nếu tìm thấy khách hàng, trả về hành động chuyển hướng đến mẫu dữ liệu của khách hàng
            action = {
                'type': 'ir.actions.act_window',
                'name': 'Customer',
                'view_mode': 'form',
                'res_model': 'res.partner',
                'res_id': customer.id,
                'target': 'new',    #thay new bằng currentđể chuyển đến model
                'context': self.env.context,
            }
            return action

    @api.depends('allday', 'start', 'stop')
    def _compute_dates(self):
        for meeting in self:
            if meeting.allday and meeting.start and meeting.stop:
                meeting.start_date = meeting.start.date()
                meeting.stop_date = meeting.stop.date()
            else:
                meeting.start_date = False
                meeting.stop_date = False

    @api.depends('stop', 'start')
    def _compute_duration(self):
        for event in self:
            event.duration = self._get_duration(event.start, event.stop)

    @api.depends('start', 'duration')
    def _compute_stop(self):
        duration_field = self._fields['duration']
        self.env.remove_to_compute(duration_field, self)
        for event in self:
            event.stop = event.start and event.start + timedelta(minutes=round((event.duration or 1.0) * 60))
            if event.allday:
                event.stop -= timedelta(seconds=1)

    def _get_duration(self, start, stop):
        if not start or not stop:
            return 0
        duration = (stop - start).total_seconds() / 3600
        return round(duration, 2)

    def confirm_selected_appointments(self):
        self.action_confirm()

    def action_confirm(self):
        for appointment in self:
            if not (appointment.partner_id and appointment.capacity and appointment.location_table and appointment.characteristic):
                raise ValidationError(_("The appointment must have complete information when confirmed."))
            appointment.write({'state': 'sale'})

    def unconfirm_selected_appointments(self):
        self.action_cancel()

    def action_cancel(self):
        self.write({'state': 'draft'})


class DishList(models.Model):
    _name = 'dish.list'
    _description = 'Dish List'

    name = fields.Char(string="Tên danh mục món ăn")


class Ingredients(models.Model):
    _name = 'ingredients.ingredients'
    _description = 'Ingredients'

    name = fields.Char(string='Tên nguyên liệu nấu ăn', is_last=True)
    description = fields.Char(string="Mô tả nguyên liệu nấu ăn")
    is_last = fields.Boolean(string='Is Last?', default=True)


class Capacity(models.Model):
    _name = 'capacity'
    _description = 'Capacity'

    name = fields.Char(required=True, string="Sức chứa của bàn")


class Characteristic(models.Model):
    _name = 'characteristic'
    _description = 'Characteristic'

    name = fields.Char(string='Characteristic', required=True)
    description = fields.Char(string="Mô tả đặc điểm bàn")


class LocationTable(models.Model):
    _name = 'location.table'
    _description = 'Location Table'

    name = fields.Char(string="Vị trí của bàn ăn", required=True)
    description = fields.Char(string="Mô tả vị trí bàn")


class Dieases(models.Model):
    _name = 'dieases.dieases'
    _description = 'Dieases'

    name = fields.Char(string='Dieases', required=True)


class Doctor(models.Model):
    _name = 'doctor.config'
    _description = 'Doctor'

    name = fields.Char(string='Doctor', required=True)
    dr_id = fields.Char(string='Doctor ID')


class Hospital(models.Model):
    _name = 'confi.hospital'
    _description = 'Hospital'

    name = fields.Char(string='Doctor', required=True)


class BloodGroup(models.Model):
    _name = 'blood.group'
    _description = 'Blood Group'

    name = fields.Char(string='Blood Group', required=True)


class Medical(models.Model):
    _name = 'medical.examination_time'
    _description = 'medical examination_time'

    name = fields.Char(string='thoi gian', required=True)
