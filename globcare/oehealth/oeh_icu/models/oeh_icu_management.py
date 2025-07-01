##############################################################################
#    Copyright (C) 2015 - Present, oeHealth (<https://www.oehealth.in>). All Rights Reserved
#    oeHealth, Hospital Management Solutions

# Odoo Proprietary License v1.0
#
# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, oeHealth.in, braincrewapps.com, or if you have received a written
# agreement from the authors of the Software.
#
# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).
#
# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.
#
# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

##############################################################################

from odoo import api, fields, models, _
import datetime
from odoo.exceptions import UserError
from datetime import date


# Intensive Care Units
class OeHealthICUConfig(models.Model):
    _name = 'oeh.medical.icu'
    _description = 'Intensive Care Units'

    ICU_TYPES = [
        ('Neonatal', 'Neonatal'),
        ('Pediatric', 'Pediatric'),
        ('Psychiatric', 'Psychiatric'),
        ('Cardiac', 'Cardiac'),
        ('Neurological', 'Neurological'),
        ('Trauma ICU', 'Trauma ICU'),
        ('Post-anesthesia', 'Post-anesthesia'),
        ('High Dependency Unit', 'High Dependency Unit'),
        ('Surgical', 'Surgical'),
        ('Mobile ICU', 'Mobile ICU'),
        ('Other', 'Other'),
    ]

    ICU_STATES = [
        ('Free', 'Free'),
        ('Reserved', 'Reserved'),
        ('Occupied', 'Occupied'),
        ('Not Available', 'Not Available'),
    ]

    CHANGE_ICU_STATUS = [
        ('Mark as Available', 'Mark as Available'),
        ('Mark as Reserved', 'Mark as Reserved'),
        ('Mark as Not Available', 'Mark as Not Available'),
    ]

    company_id = fields.Many2one(
        'res.company', store=True, default=lambda self: self.env.company
    )
    name = fields.Char(string='ICU #', size=128, required=True)
    institution = fields.Many2one('oeh.medical.health.center', string='Health Center')
    icu_type = fields.Selection(ICU_TYPES, string='Type of ICU', required=True)
    icu_charge = fields.Float(string='ICU Admission Charge (per day)')
    building = fields.Many2one('oeh.medical.health.center.building', string='Building', domain="[('institution', '=', institution)]")
    floor = fields.Integer(string='Floor Number')
    telephone = fields.Boolean(string='Telephone access')
    ac = fields.Boolean(string='Air Conditioning')
    private_bathroom = fields.Boolean(string='Private Bathroom')
    guest_sofa = fields.Boolean(string='Guest sofa-bed')
    tv = fields.Boolean(string='Television')
    internet = fields.Boolean(string='Internet Access')
    refrigerator = fields.Boolean(string='Refrigerator')
    microwave = fields.Boolean(string='Microwave')
    equipment_mechanical_ventilator = fields.Boolean(string='Mechanical Ventilators')
    equipment_cardiac_monitors = fields.Boolean('Cardiac Monitors')
    equipment_intravenous_lines = fields.Boolean('Intravenous Lines')
    equipment_feeding_tubes = fields.Boolean('Feeding Tubes')
    equipment_nasogastric_tubes = fields.Boolean('Nasogastric Tubes')
    equipment_suction_pumps = fields.Boolean('Suction Pumps')
    equipment_drains = fields.Boolean('Drains')
    equipment_catheters = fields.Boolean('Catheters')
    info = fields.Text(string='Extra Info')
    state = fields.Selection(ICU_STATES, string='Status', default=lambda *a: 'Free')
    change_icu_status = fields.Selection(CHANGE_ICU_STATUS, string='Change ICU Status')

    @api.onchange('change_icu_status', 'state')
    def onchange_icu_status(self):
        res = {}
        if self.state and self.change_icu_status:
            if self.state == "Occupied":
                raise UserError(_('ICU status can not change if it already occupied!'))
            else:
                if self.change_icu_status == "Mark as Reserved":
                    self.state = "Reserved"
                elif self.change_icu_status == "Mark as Available":
                    self.state = "Free"
                else:
                    self.state = "Not Available"
        return res

    # Preventing deletion of a ICUs which is not in draft state
    def unlink(self):
        for icus in self.filtered(lambda icus: icus.state not in ['Free', 'Not Available']):
            raise UserError(_('You can not delete ICU which is in "Reserved" or "Occupied" state !!'))
        return super(OeHealthICUConfig, self).unlink()

    def write(self, vals):
        if 'change_icu_status' in vals:
            if vals.get('change_icu_status') in ('Mark as Reserved', 'Mark as Not Available'):
                for icus in self.filtered(lambda icus: icus.state in ['Occupied']):
                    raise UserError(_('ICU status can not change if it already occupied!'))
        return super(OeHealthICUConfig, self).write(vals)

# Glasgow Check
class OeHealthGlasgow(models.Model):
    _name = 'oeh.medical.icu.glasgow'
    _description = 'Check Glasgow Coma Scale'

    EYES = [
        ('1', '1 : Does not Open Eyes'),
        ('2', '2 : Opens eyes in response to painful stimuli'),
        ('3', '3 : Opens eyes in response to voice'),
        ('4', '4 : Opens eyes spontaneously'),
    ]

    VERBAL = [
        ('1', '1 : Makes no sounds'),
        ('2', '2 : Incomprehensible sounds'),
        ('3', '3 : Utters inappropriate words'),
        ('4', '4 : Confused, disoriented'),
        ('5', '5 : Oriented, converses normally'),
    ]

    MOTOR = [
        ('1', '1 : Makes no movement'),
        ('2', '2 : Extension to painful stimuli - decerebrate response -'),
        ('3', '3 : Abnormal flexion to painful stimuli (decorticate response)'),
        ('4', '4 : Flexion / Withdrawal to painful stimuli'),
        ('5', '5 : localizes painful stimuli'),
        ('6', '6 : Obeys commands'),
    ]

    name = fields.Char(string='GCS Evalution #', size=128, required=True, default=lambda *a: '/')
    date = fields.Datetime(string='Date & Time', required=True, default=lambda *a: datetime.datetime.now())
    glasgow = fields.Integer(string='Score')
    glasgow_eyes = fields.Selection(EYES, string='Eyes', default=lambda *a: '4')
    glasgow_verbal = fields.Selection(VERBAL, string='Verbal', default=lambda *a: '5')
    glasgow_motor = fields.Selection(MOTOR, string='Motor', default=lambda *a: '6')
    rounding_id = fields.Many2one('oeh.medical.icu.admission.rounding', string='Rounding #', index=True, ondelete="cascade")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('oeh.medical.icu.glasgow') or '/'
        return super(OeHealthGlasgow, self).create(vals)

    @api.onchange('glasgow_verbal', 'glasgow_motor', 'glasgow_eyes')
    def onchange_glasgow_values(self):
        self.glasgow = int(self.glasgow_eyes) + int(self.glasgow_verbal) + int(self.glasgow_motor)


# ApacheII Scoring
class OeHealthApacheIIScoring(models.Model):
    _name = 'oeh.medical.icu.apache2'
    _description = 'ApacheII Scoring'

    ADMISSION_TYPE = [
        ('Medical or emergency postoperative', 'Medical or emergency postoperative'),
        ('Elective postoperative', 'Elective postoperative'),
        ('N/A', 'N/A')
    ]

    name = fields.Char(string='ASO #', size=128, required=True, default=lambda *a: '/')
    date = fields.Datetime(string='Date & Time', required=True, default=lambda *a: datetime.datetime.now())
    temperature = fields.Float('Rectal temperature')
    mean_ap = fields.Integer('Mean Arterial Pressure')
    heart_rate = fields.Integer('Heart Rate')
    respiratory_rate = fields.Integer('Respiratory Rate')
    fio2 = fields.Float('FiO2')
    pao2 = fields.Integer('PaO2')
    paco2 = fields.Integer('PaCO2')
    aado2 = fields.Integer('A-a DO2')
    ph = fields.Float('pH')
    serum_sodium = fields.Integer('Sodium')
    serum_potassium = fields.Float('Potassium')
    serum_creatinine = fields.Float('Creatinine')
    arf = fields.Boolean('Acute Renal Failure')
    wbc = fields.Float('WBC/ml')
    hematocrit = fields.Float('Hematocrit')
    gcs = fields.Integer('Last Glasgow Coma Scale')
    chronic_condition = fields.Boolean('Chronic condition', help='Organ Failure or immunocompromised patient')
    admission_type = fields.Selection('Admission Type')
    score = fields.Integer('Score')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('oeh.medical.icu.apache2') or '/'
        return super(OeHealthApacheIIScoring, self).create(vals)


# ICU Admission Management
class OeHealthICUAdmissions(models.Model):
    _name = 'oeh.medical.icu.admission'
    _description = 'ICU Admission Management'

    ADMISSION_STATES = [
        ('Draft', 'Draft'),
        ('Hospitalized', 'Hospitalized'),
        ('On Ventilation', 'On Ventilation'),
        ('Ventilation Removed', 'Ventilation Removed'),
        ('Discharged', 'Discharged'),
        ('Invoiced', 'Invoiced'),
        ('Cancelled', 'Cancelled')
    ]

    VENTILATION_TYPE = [
        ('Non-Invasive Positive Pressure', 'Non-Invasive Positive Pressure'),
        ('ETT - Endotracheal Tube', 'ETT - Endotracheal Tube'),
        ('Tracheostomy', 'Tracheostomy'),
    ]

    # Automatically detect logged in physician
    def _get_physician(self):
        """Return default physician value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    def _get_ventilation_duration(self):
        def compute_duration_from_dates(ventilation_start_date, ventilation_end_date):
            # ventilation_start_date = datetime.datetime.strptime(str(ventilation_start_date), '%Y-%m-%d %H:%M:%S')
            if ventilation_end_date:
                # ventilation_end_date = datetime.datetime.strptime(str(ventilation_end_date), '%Y-%m-%d %H:%M:%S')
                delta = ventilation_end_date - ventilation_start_date
                print(delta)
                days = int(delta.days)
                print(days)
            else:
                now = datetime.datetime.now()
                delta = now - ventilation_start_date
                print('2..', delta)
                days = int(delta.days)
                print('2..', days)

            return days

        for patient_data in self:
            if patient_data.ventilation_start_date:
                patient_data.ventilation_duration = compute_duration_from_dates(patient_data.ventilation_start_date, patient_data.ventilation_end_date)
            else:
                patient_data.ventilation_duration = 0
        return True

    company_id = fields.Many2one(
        'res.company', store=True, default=lambda self: self.env.company
    )
    name = fields.Char(string='ICU Admission #', size=128, required=True, default=lambda *a: '/')
    icu_room = fields.Many2one('oeh.medical.icu', domain="[('state','=','Free')]", string='ICU Room #', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True, readonly=True, states={'Draft': [('readonly', False)]})
    admission_reason = fields.Many2one('oeh.medical.pathology', string='Reason for Admission', help="Reason for Admission", required=True, readonly=True, states={'Draft': [('readonly', False)]})
    admission_date = fields.Datetime(string='Hospitalization Date', readonly=True, states={'Draft': [('readonly', False)]})
    discharge_date = fields.Datetime(string='Discharge Date', readonly=True, states={'Hospitalized': [('readonly', False)], 'On Ventilation': [('readonly', False)], 'Ventilation Removed': [('readonly', False)]})
    attending_physician = fields.Many2one('oeh.medical.physician', string='Attending Doctor', readonly=True, states={'Draft': [('readonly', False)]}, default=_get_physician)
    operating_physician = fields.Many2one('oeh.medical.physician', string='Operating Doctor', readonly=True, states={'Draft': [('readonly', False)]})
    admission_condition = fields.Text(string='Condition before Admission', readonly=True, states={'Draft': [('readonly', False)]})
    info = fields.Text(string='Extra Info', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    ventilation_type = fields.Selection(VENTILATION_TYPE, string='Ventilation Type', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    ett_size = fields.Integer(string='ETT Size', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    tracheostomy_size = fields.Integer(string='Tracheostomy size', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    ventilation_remarks = fields.Char(string='Remarks', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    ventilation_start_date = fields.Datetime(string='From Date', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    ventilation_end_date = fields.Datetime(string='End Date', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    ventilation_duration = fields.Integer(compute=_get_ventilation_duration, string='Duration')
    rounding_lines = fields.One2many('oeh.medical.icu.admission.rounding', 'admission_id', string='Rounding', readonly=True, states={'Hospitalized': [('readonly', False)], 'On Ventilation': [('readonly', False)], 'Ventilation Removed': [('readonly', False)]})
    state = fields.Selection(ADMISSION_STATES, string='State', default=lambda *a: 'Draft')

    @api.model
    def create(self, vals):
        company = self.env['res.company']._company_default_get('oeh.medical.icu.admission')
        search_sequence = self.env['ir.sequence'].search(
            [('code', '=', 'oeh.medical.icu.admission'), ('company_id', 'in', [company.id, False])], order='company_id')
        if not search_sequence:
            values = {
                'name': 'ICU - Admissions (' + str(company.name) + ')',
                'code': 'oeh.medical.icu.admission',
                'company_id': company.id,
                'prefix': 'ICU-ADM-',
                'padding': 5,
            }
            self.env['ir.sequence'].sudo().create(values)
            vals['name'] = self.env['ir.sequence'].next_by_code('oeh.medical.icu.admission')
            medical_icu_admission = models.Model.create(self, vals)
            return medical_icu_admission
        else:
            sequence = self.env['ir.sequence'].next_by_code('oeh.medical.icu.admission')
            vals['name'] = sequence or '/'
            return super(OeHealthICUAdmissions, self).create(vals)

    def set_to_hospitalized(self):
        hospitalized_date = False
        for ina in self:
            if ina.admission_date:
                hospitalized_date = ina.admission_date
            else:
                hospitalized_date = datetime.datetime.now()

            if ina.icu_room:
                query = _("update oeh_medical_icu set state='Occupied' where id=%s") % (str(ina.icu_room.id))
                self.env.cr.execute(query)
        return self.write({'state': 'Hospitalized', 'admission_date': hospitalized_date})

    def set_to_ventilation(self):
        return self.write({'state': 'On Ventilation', 'ventilation_start_date': datetime.datetime.now(), 'ventilation_end_date': False})

    def remove_ventilation(self):
        return self.write({'state': 'Ventilation Removed', 'ventilation_end_date': datetime.datetime.now()})

    def set_to_discharged(self):
        discharged_date = False
        for ina in self:
            if ina.discharge_date:
                discharged_date = ina.discharge_date
            else:
                discharged_date = datetime.datetime.now()

            if ina.icu_room:
                query = _("update oeh_medical_icu set state='Free' where id=%s") % (str(ina.icu_room.id))
                self.env.cr.execute(query)
        return self.write({'state': 'Discharged', 'discharge_date': discharged_date})

    def set_to_cancelled(self):
        bed_obj = self.env["oeh.medical.health.center.beds"]
        for ina in self:
            if ina.icu_room:
                query = _("update oeh_medical_icu set state='Free' where id=%s") % (str(ina.icu_room.id))
                self.env.cr.execute(query)
        return self.write({'state': 'Cancelled'})

    def set_to_draft(self):
        return self.write({'state': 'Draft'})

    def _default_account(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        print(journal.default_credit_account_id)
        return journal.default_credit_account_id.id

    def set_to_invoiced(self):
        invoice_obj = self.env["account.move"]
        invoice_line_obj = self.env["account.move.line"]
        inv_ids = []
        res = {}

        for inpatient in self:

            # Calculate Hospitalized duration
            duration = 1

            if inpatient.admission_date and inpatient.discharge_date:
                admission_date = inpatient.admission_date #datetime.datetime.strptime(inpatient.admission_date, "%Y-%m-%d %H:%M:%S")
                discharge_date = inpatient.discharge_date #datetime.datetime.strptime(inpatient.discharge_date, "%Y-%m-%d %H:%M:%S")
                delta = date(discharge_date.year, discharge_date.month, discharge_date.day) - date(admission_date.year, admission_date.month, admission_date.day)
                if delta.days == 0:
                    duration = 1
                else:
                    duration = delta.days

            # Create Invoice
            if inpatient.icu_room:
                curr_invoice = {
                    'partner_id': inpatient.patient.partner_id.id,
                    # 'account_id': inpatient.patient.partner_id.property_account_receivable_id.id,
                    'patient': inpatient.patient.id, 'state': 'draft',
                    'move_type': 'out_invoice',
                    'invoice_date': datetime.datetime.now(),
                    # 'origin': "ICU Admission# : " + inpatient.name,
                    'invoice_sequence_number_next_prefix': False
                }

                inv_ids = invoice_obj.create(curr_invoice)

                prd_account_id = self._default_account()
                print(prd_account_id)

                # Create Invoice line
                curr_invoice_line = {
                    'name': "ICU Admission charge for " + str(duration) + " day(s) admission in " + inpatient.icu_room.name,
                    'price_unit': duration * inpatient.icu_room.icu_charge,
                    'quantity': 1.0,
                    'account_id': prd_account_id,
                    'move_id': inv_ids.id,
                }
                inv_line_ids = invoice_line_obj.create(curr_invoice_line)
                res = self.write({'state': 'Invoiced'})

            else:
                raise UserError(_('Please first select ICU room to raise an invoice !'))
        return res


# ICU Admission Rounding Management
class OeHealthICUAdmissionRoundings(models.Model):
    _name = 'oeh.medical.icu.admission.rounding'
    _description = 'ICU Admission Rounding'

    PUPIL_DIALATION = [
        ('Normal', 'Normal'),
        ('Miosis', 'Miosis'),
        ('Mydriasis', 'Mydriasis')
    ]

    REACTIVITY = [
        ('Brisk', 'Brisk'),
        ('Sluggish', 'Sluggish'),
        ('Nonreactive', 'Nonreactive')
    ]

    RESPIRATION_TYPE = [
        ('Intercostal', 'Intercostal'),
        ('Labored', 'Labored'),
        ('Shallow', 'Shallow'),
        ('Deep', 'Deep'),
        ('Regular', 'Regular'),
        ('None', 'None')
    ]

    CHEST_EXPANSION = [
        ('Symmetrical', 'Symmetrical'),
        ('Asymmetrical', 'Asymmetrical')
    ]

    TRACHE = [
        ('Midline', 'Midline'),
        ('Deviated right', 'Deviated right'),
        ('Deviated left', 'Deviated left')
    ]

    VENOUS_ACCESS = [
        ('None', 'None'),
        ('Central catheter',
         'Central catheter'),
        ('Peripheral', 'Peripheral')
    ]

    VOMITING = [
        ('No', 'No'),
        ('Vomiting', 'Vomiting'),
        ('Vomiting with Blood', 'Vomiting with Blood')
    ]

    BOWEL_SOUND = [
        ('Normal', 'Normal'),
        ('Increased', 'Increased'),
        ('Decreased', 'Decreased'),
        ('Absent', 'Absent')
    ]

    STOOL = [
        ('Normal', 'Normal'),
        ('Constipation', 'Constipation'),
        ('Diarrhea', 'Diarrhea'),
        ('Melena (Black tarry stools)', 'Melena (Black tarry stools)')
    ]

    company_id = fields.Many2one(
        'res.company', store=True, default=lambda self: self.env.company
    )

    name = fields.Char(string='Rounding #', size=128, required=True, default=lambda *a: '/')
    admission_id = fields.Many2one('oeh.medical.icu.admission', string='ICU Admission #', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    date = fields.Datetime(string='Date & Time', required=True, readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]}, default=lambda *a: datetime.datetime.now())
    health_professional = fields.Many2one('res.users', string='Health Professionals', required=True, readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]}, default=lambda self: self._uid)
    patient = fields.Many2one('oeh.medical.patient', related='admission_id.patient', string='Patient', help="Patient Name", readonly=True, store=True)
    pupil_dilation = fields.Selection(PUPIL_DIALATION, string='Pupil Dilation', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    left_pupil = fields.Integer(string='Left pupil size (in mm)', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    right_pupil = fields.Integer(string='Right pupil size (in mm)', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    anisocoria = fields.Boolean(string='Anisocoria', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    pupil_reactivity = fields.Selection(REACTIVITY, string='Pupil Reactivity', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    respiration = fields.Selection(RESPIRATION_TYPE, string='Respiration', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    oxygen_mask = fields.Boolean(string='Oxygen Mask', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    fio2 = fields.Integer(string='FiO2', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    peep = fields.Boolean(string='Peep', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    peep_pressure = fields.Integer(string='Peep Pressure (cm H2O)', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    sce = fields.Boolean(string='Subcutaneous Emphysema', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    lips_lesion = fields.Boolean(string='Lips lesion', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    oral_mucosa_lesion = fields.Boolean(string='Oral mucosa lesion', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    chest_expansion = fields.Selection(CHEST_EXPANSION, string='Chest Expansion', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    paradoxical_expansion = fields.Boolean(string='Paradoxical Chest Expansion', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    tracheal_tug = fields.Boolean(string='Tracheal Tug', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    trachea_alignment = fields.Selection(TRACHE, string='Tracheal alignment', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    venous_access = fields.Selection(VENOUS_ACCESS, string='Venous Access', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    swan_ganz = fields.Boolean(string='Swan Ganz', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    arterial_access = fields.Boolean('Arterial Access', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    dialysis = fields.Boolean(string='Dialysis', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    bacteremia = fields.Boolean(string='Presence of bacteria in the blood', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    surgery_infection = fields.Boolean(string='Surgery Infection', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    wound_dehiscence = fields.Boolean(string='Wound Dehiscence', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    cellulitis = fields.Boolean(string='Cellulitis (Bacterial skin infection)', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    vomiting = fields.Selection(VOMITING, string='Vomiting', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    bowel_sounds = fields.Selection(BOWEL_SOUND, string='Bowel Sound', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    stools = fields.Selection(STOOL, string='Stools', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    xray = fields.Binary(string='Xray', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    gcs_lines = fields.One2many('oeh.medical.icu.glasgow', 'rounding_id', string='Glasgow Coma Scales', readonly=False, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]})
    state = fields.Selection(related='admission_id.state', string='State', default=lambda *a: 'Draft', store=True)

    @api.onchange('left_pupil', 'right_pupil')
    def onchange_pupil_values(self):
        if self.left_pupil == self.right_pupil:
            self.anisocoria = False
        else:
            self.anisocoria = True

    @api.model
    def create(self, vals):
        company = self.env['res.company']._company_default_get('oeh.medical.icu.admission.rounding')
        search_sequence = self.env['ir.sequence'].search(
            [('code', '=', 'oeh.medical.icu.admission.rounding'), ('company_id', 'in', [company.id, False])],
            order='company_id')
        if not search_sequence:
            values = {
                'name': 'ICU - Rounding (' + str(company.name) + ')',
                'code': 'oeh.medical.icu.admission.rounding',
                'company_id': company.id,
                'prefix': 'ICUR/' + datetime.datetime.now().strftime('%m-%d-%Y') + '/',
                'padding': 5,
            }
            self.env['ir.sequence'].sudo().create(values)
            vals['name'] = self.env['ir.sequence'].next_by_code('oeh.medical.icu.admission.rounding')
            medical_icu_admission_rounding = models.Model.create(self, vals)
            return medical_icu_admission_rounding
        else:
            sequence = self.env['ir.sequence'].next_by_code('oeh.medical.icu.admission.rounding')
            vals['name'] = sequence or '/'
            return super(OeHealthICUAdmissionRoundings, self).create(vals)
