from odoo import fields, models, api
from datetime import timedelta


class ReservationTime(models.Model):
    _name = 'reservation.time'
    _description = 'Reservation Time'

    table_id = fields.Many2one('manager.table', string='Table', required=True, ondelete='cascade')
    # table_name = fields.Char(string='Table Name', related='table_id.name', readonly=True)
    capacity = fields.Many2one(comodel_name="capacity", string="Sức chứa của bàn")
    location_table = fields.Many2one(comodel_name="location.table", string="Vị trí của bàn ăn")
    characteristic = fields.Many2one(comodel_name="characteristic", string="Đặc điểm của bàn ăn")

    start = fields.Datetime(string='Start time', required=True, tracking=True)
    stop = fields.Datetime(string='End time', required=True, tracking=True, store=True, compute='_compute_stop')
    allday = fields.Boolean('All Day', default=False)
    start_date = fields.Date(string='Start Date', store=True, tracking=True, compute='_compute_dates')
    stop_date = fields.Date(string='End Date', store=True, tracking=True, compute='_compute_dates')
    duration = fields.Float('Duration', compute='_compute_duration', store=True, readonly=False)

    appointment_id = fields.Many2one('patient.appointment', string="Appointment")

    # @api.depends('allday', 'start', 'stop')
    # def _compute_dates(self):
    #     for meeting in self:
    #         if meeting.allday and meeting.start and meeting.stop:
    #             meeting.start_date = meeting.start.date()
    #             meeting.stop_date = meeting.stop.date()
    #         else:
    #             meeting.start_date = False
    #             meeting.stop_date = False

    @api.depends('allday', 'start')
    def _compute_dates(self):
        for meeting in self:
            if meeting.start:
                meeting.start_date = meeting.start.date()
                meeting.stop_date = (
                            meeting.start + timedelta(days=1)).date() if meeting.allday else meeting.start.date()

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


