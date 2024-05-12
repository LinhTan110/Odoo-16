from odoo import models, fields


class AppointmentAppointment(models.Model):
    _name = 'appointment.appointment'
    _description = 'Appointment'

    hospital = fields.Many2one(comodel_name='confi.hospital', string='Hospital')
    dr_nm = fields.Many2one(comodel_name='doctor.config', string='Doctor')
    date = fields.Date(string='Date')
    time = fields.Char(string='Time')
    patient_info_id = fields.Many2one(comodel_name='patient.information', string='Patient')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    mobile = fields.Char(string='Mobile')
    email = fields.Char(string='Email')
    blood_id = fields.Many2one(comodel_name='blood.group', string='Blood Group')
    diseases = fields.Many2one(comodel_name='dieases.dieases', string='Disease')


class PatientInformation(models.Model):
    _name = 'patient.information'
    _description = 'Patient Information'

    name = fields.Char(string='Name')
    date_of_birth = fields.Date(string='Date of Birth')