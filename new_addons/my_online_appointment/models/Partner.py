from odoo import fields, models, api, _


class KeThuaPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Ke Thua Partner'

    email = fields.Char(string='Email')
    appointment_id = fields.Many2one(comodel_name="patient.appointment", string="Appointment")
    position = fields.Selection([('admin', 'Admin'), ('employee', 'Employee'), ('user', 'User')], string="Position",
                                tracking=True, default='user')

    def action_create_appointment(self):
        return {
            'name': _('Appointment Customer'),
            'view_mode': 'form',
            'res_model': 'patient.appointment',
            'type': 'ir.actions.act_window',
            'context': {
                'default_name': self.name or False,
                'default_email': self.email or False,
                'default_phone': self.phone or False,
            },
            'target': 'new'
        }

    def action_view_appointments(self):
        action = self.env.ref('mbs_online_appointment.action_patient_appointment').read()[0]
        action['domain'] = [('name', '=', self.name), ('email', '=', self.email), ('phone', '=', self.phone)]
        return action

    # @api.onchange('name', 'email', 'phone')
    # def _onchange_partner_info(self):
    #     if self.appointment_id:
    #         self.appointment_id.write({
    #             'name': self.name,
    #             'email': self.email,
    #             'phone': self.phone,
    #             # Cập nhật các trường thông tin khác tùy theo yêu cầu của bạn
    #         })

    # def action_create_appointment(self):
    #     appointment_vals = {
    #         'name': self.name,
    #         'email': self.email,
    #         'phone': self.phone,
    #         # Cập nhật các trường thông tin khác tùy theo yêu cầu của bạn
    #     }
    #     appointment = self.env['patient.appointment'].create(appointment_vals)
    #     # self.appointment_id = appointment.id
    #     self.appointment_id = appointment and appointment.id or False
    #
    #     return {
    #         'name': _('Appointment Information'),
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'patient.appointment',
    #         # 'res_id': appointment.id,
    #         'res_id': appointment and appointment.id or False,
    #         'type': 'ir.actions.act_window',
    #         'target': 'current',
    #     }


class HrEmployeeExtension(models.Model):
    _inherit = 'hr.employee'

    employee_type = fields.Selection(
        selection_add=[
            ('chef', 'Chef'),
            ('serve', 'Serve'),
        ],
        ondelete={
            'chef': 'set default',
            'serve': 'set default',
        }
    )
    note = fields.Text(string="Note", help="A note field for additional employee information.")