# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
import base64
import json


class TestForm(http.Controller):
    @http.route(['/detail-table/<int:table_id>'], type='http', auth="public", website=True)
    def test(self, table_id, **kw):
        table = http.request.env['manager.table'].browse(table_id)
        location_table = table.location_table
        related_tables = http.request.env['manager.table'].search([
            ('location_table', '=', location_table.id),
            ('id', '!=', table_id)  # Loại bỏ bàn hiện đang xem khỏi kết quả)
        ])
        related_tables = related_tables[:4]  # Chỉ lấy tối đa 4 bàn liên quan
        return request.render("my_online_appointment.detail_table_form",{
            'table': table,
            'related_tables': related_tables
        })


class DetailPartnerForm(http.Controller):
    @http.route(['/detail-employee/<int:employee_id>'], type='http', auth="public", website=True)
    def partner(self, employee_id, **kw):
        employee = http.request.env['hr.employee'].browse(employee_id)
        employee_type = employee.employee_type
        similar_employees = http.request.env['hr.employee'].search([
            ('employee_type', '=', employee_type),
            # ('id', '!=', employee_id)  # Loại bỏ đối tác hiện tại khỏi kết quả
        ])
        similar_employees = similar_employees[:4]  # Chỉ lấy tối đa 4 bàn liên quan
        return request.render("my_online_appointment.detail_employee_form", {
            'employee': employee,
            'similar_employees': similar_employees
        })



class Table(http.Controller):
    @http.route('/table', type='http', auth='public', website=True)
    def table(self, **kw):
        tables = http.request.env['manager.table'].search([])
        return http.request.render('my_online_appointment.table_form', {
            'tables': tables,
        })


class HomeForm(http.Controller):
    @http.route(['/'], type='http', auth="public", website=True)
    def home(self, **kw):
        chefs = request.env['hr.employee'].sudo().search([('employee_type', '=', 'chef')])
        serves = request.env['hr.employee'].sudo().search([('employee_type', '=', 'serve')])
        chefs = chefs[:4]
        serves = serves[:4]
        tables = http.request.env['manager.table'].sudo().search([('location_table', '=', 'Bên cửa sổ')], limit=4)
        positions = http.request.env['res.partner'].search([('position', '=', 'employee')])
        positions = positions[:3]
        return request.render('my_online_appointment.PageHome_inherit', {
            'positions': positions,
            'tables': tables,
            'chefs': chefs,
            'serves': serves,
        })

class Policy(http.Controller):
    @http.route('/policy', type='http', auth='public', website=True)
    def policy(self, **kw):
        policys = http.request.env['restaurant.policy'].sudo().search([])
        return http.request.render('my_online_appointment.policy_form', {
            'policys': policys,
        })


class Datlich(http.Controller):
    @http.route(['/datlich'], type='http', auth="public", website=True)
    def datlich(self, **kw):
        user = request.env.user  # Lấy thông tin của tài khoản đang đăng nhập
        default_name = user.name if user else ''
        default_email = user.email if user else ''
        default_phone = user.phone if user else ''
        default_restaurant = http.request.env['restaurant.name'].sudo().search([], limit=1).name
        default_address = self._get_address(default_restaurant)
        capacitys = http.request.env['capacity'].search([])
        locations = http.request.env['location.table'].search([])
        characteristics = http.request.env['characteristic'].search([])
        return http.request.render('my_online_appointment.Datlich_form', {
            'capacitys': capacitys,
            'locations': locations,
            'characteristics': characteristics,
            'default_name': default_name,
            'default_email': default_email,
            'default_phone': default_phone,
            'default_restaurant': default_restaurant,
            'default_address': default_address,
        })

    def _get_address(self, restaurant_name):
        restaurant = request.env['restaurant.name'].sudo().search([('name', '=', restaurant_name)], limit=1)        # Tìm kiếm địa chỉ dựa trên tên nhà hàng
        if restaurant:
            return restaurant.address
        else:
            return ''

    @http.route(['/update_address'], type='http', auth='public', website=True)
    def update_address(self, **post):
        if post.get('restaurant_name'):
            restaurant_name = post.get('restaurant_name')
            address = self._get_address(restaurant_name)
            if address:
                record_id = int(post.get('record_id'))      # Lấy id của bản ghi trong model và cập nhật địa chỉ
                request.env['restaurant.name'].sudo().browse(record_id).write({'address': address})


class OnlineSuccessForm(http.Controller):
    @http.route(['/success'], type='http', auth="public", website=True)
    def final_submission(self, **kw):
        user = request.env.user  # Lấy thông tin của tài khoản đang đăng nhập
        default_name = user.name if user else ''
        default_email = user.email if user else ''
        default_phone = user.phone if user else ''
        # Lấy thông tin nhà hàng đầu tiên
        restaurant = request.env['restaurant.name'].sudo().search([], limit=1)
        default_restaurant = restaurant.name if restaurant else ''
        default_restaurant_email = restaurant.email if restaurant else ''
        default_restaurant_phone = restaurant.phone if restaurant else ''
        default_address = self._get_address(default_restaurant)
        return request.render("my_online_appointment.thank_you_template_id_inherit", {
            'default_name': default_name,
            'default_email': default_email,
            'default_phone': default_phone,
            'default_restaurant': default_restaurant,
            'default_restaurant_email': default_restaurant_email,
            'default_restaurant_phone': default_restaurant_phone,
            'default_address': default_address,
        })

    def _get_address(self, restaurant_name):
        restaurant = request.env['restaurant.name'].sudo().search([('name', '=', restaurant_name)], limit=1)        # Tìm kiếm địa chỉ dựa trên tên nhà hàng
        if restaurant:
            return restaurant.address
        else:
            return ''


class AppointmentController(http.Controller):
    @http.route('/search_tables', type='json', auth='public', methods=['POST'], website=True)
    def search_tables(self, **kw):
        # Parse request parameters
        capacity = int(kw.get('capacity'))
        location_table = int(kw.get('location_table'))
        characteristic = int(kw.get('characteristic'))
        start = kw.get('start')
        duration = kw.get('duration')
        allday = kw.get('allday')
        try:
            if allday:
                start_datetime = datetime.strptime(start, "%Y-%m-%d")
            else:
                start_datetime = datetime.strptime(start, "%Y-%m-%dT%H:%M")
                start_datetime -= timedelta(hours=7)
        except ValueError as e:
            print('Error:', e)
            return http.request.redirect('/error')
        try:
            if allday:
                end_datetime = start_datetime + timedelta(days=1)
            else:
                end_datetime = start_datetime + timedelta(hours=float(duration))
            existing_reservations = http.request.env['reservation.time'].search([
                ('start', '<', end_datetime),
                ('stop', '>', start_datetime)
            ])
            booked_tables_ids = existing_reservations.mapped('table_id.id')
            domain = [
                ('capacity', '=', capacity),
                ('location_table', '=', location_table),
                ('characteristic', '=', characteristic),
                ('id', 'not in', booked_tables_ids)
            ]
            matched_tables = http.request.env['manager.table'].search(domain)
            tables_info = [{'id': table.id, 'name': table.name} for table in matched_tables]

            return {'available_tables': tables_info}
        except Exception as e:
            print('Error:', e)

    @http.route(['/create_appointment'], type='http', auth="public", website=True, csrf=False)
    def final_create(self, **kw):
        if kw.get('name'):
            # table_id = kw.get('table_id')
            # table = request.env['manager.table'].sudo().search([('id', '=', table_id)], limit=1)
            order = request.website.sale_get_order()
            name = kw.get('name')
            phone = kw.get('phone')
            email = kw.get('email')
            start = kw.get('start')
            duration = kw.get('duration')
            allday = kw.get('allday', False) == 'true'  # Xử lý checkbox
            capacity = kw.get('capacity')
            location_table = kw.get('location_table')
            characteristic = kw.get('characteristic')
            note = kw.get('note')
            restaurant_name = kw.get('restaurant_name')
            restaurant = http.request.env['restaurant.name'].sudo().search([('name', '=', restaurant_name)], limit=1)
            if not restaurant:
                print("Không tìm thấy nhà hàng có tên:", restaurant_name)
                return http.request.redirect('/error')  # Hoặc xử lý lỗi khác tùy theo yêu cầu của bạn
            restaurant_id = restaurant.id
            try:
                if allday:
                    start_datetime = datetime.strptime(start, "%Y-%m-%d")
                else:
                    start_datetime = datetime.strptime(start, "%Y-%m-%dT%H:%M")
                    start_datetime -= timedelta(hours=7)
            except ValueError as e:
                print('Error:', e)
                return http.request.redirect('/error')
            try:
                if allday:
                    end_datetime = start_datetime + timedelta(days=1)
                else:
                    end_datetime = start_datetime + timedelta(hours=float(duration))
                appointment_vals = {
                    'name': name,
                    'phone': phone,
                    'email': email,
                    'start': start_datetime,
                    'stop': end_datetime,
                    'duration': duration if not allday else False,
                    'allday': allday,
                    'capacity': capacity,
                    'location_table': location_table,
                    'characteristic': characteristic,
                    'note': note,
                    'restaurant_name': restaurant_id,
                    'product_ids': [(6, 0, order.order_line.mapped('product_id').ids if order else [])],

                    # 'manager_table': table,
                }
                if allday:      # Nếu chọn All Day, cập nhật trường start_date
                    appointment_vals['start_date'] = start_datetime.date()
                appointment = http.request.env['patient.appointment'].create(appointment_vals)
                appointment.write({'start': start_datetime})
            except Exception as e:
                print('Error:', e)
                return http.request.redirect('/error')
            return http.request.redirect('/success')
        return http.request.redirect('/datlich')


class WebsiteSaleCustom(WebsiteSale):
    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        response = super(WebsiteSaleCustom, self).address(**kw)
        default_restaurant = request.env['restaurant.name'].sudo().search([], limit=1)
        capacitys = request.env['capacity'].search([])
        locations = request.env['location.table'].search([])
        characteristics = request.env['characteristic'].search([])
        response.qcontext.update({
            'capacitys': capacitys,
            'locations': locations,
            'characteristics': characteristics,
        })
        if default_restaurant:
            response.qcontext['default_restaurant'] = default_restaurant.name
            response.qcontext['default_address'] = default_restaurant.address
        else:
            response.qcontext['default_restaurant'] = 'Không tìm thấy nhà hàng mặc định'
            response.qcontext['default_address'] = 'Không có địa chỉ'
        return response

    def _get_address(self, restaurant_name):
        restaurant = request.env['restaurant.name'].sudo().search([('name', '=', restaurant_name)], limit=1)
        if restaurant:
            return restaurant.address
        return ''


class CustomSignupController(AuthSignupHome):
    @http.route('/web/signup', type='http', auth='public', website=True, csrf=False)
    def web_auth_signup(self, *args, **kw):
        response = super(CustomSignupController, self).web_auth_signup(*args, **kw)
        if request.httprequest.method == 'POST' and kw.get('phone'):
            user = request.env['res.users'].sudo().search([('login', '=', kw.get('login'))], limit=1)
            if user:
                user.partner_id.phone = kw.get('phone')
        return response


