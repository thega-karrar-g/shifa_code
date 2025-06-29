from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ShifaWoundAssessment(models.Model):
    _name = 'sm.shifa.wound.assessment.values'
    _description = "Wound Assessment Values for Patient"

    # Wound Assessment
    wound_assessment_show = fields.Boolean()
    wound_number = fields.Integer(String="Wound number")
    analgesia_pre_dressing = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('NA', 'NA'),
        ], String="Analgesia pre dressing")

    # Wound Base
    wound_base_necrotic = fields.Float(string="Necrotic (%)")
    wound_base_stough_yellow = fields.Float(string="Slough (yellow) (%)")
    wound_base_granulation_red = fields.Float(string="Granulation (red) (%)")
    wound_base_epithelialisation_pink = fields.Float(string="Epithelialisation (pink) (%)")
    wound_base_other_choose = fields.Boolean(string="Other")
    wound_base_other_content = fields.Char()
    wound_base_other = fields.Float(string="(%)")
    exudate_volume = fields.Selection([
        ('Minimal', 'Minimal'),
        ('Moderate', 'Moderate'),
        ('Heavy', 'Heavy'),
        ('Nil', 'Nil'),
        ('NA', 'NA'),
    ], string="Exudate Volume")
    exudate_type = fields.Selection([
        ('Hemoserous', 'Hemoserous'),
        ('Serous', 'Serous'),
        ('Purulent', 'Purulent'),
        ('Blood', 'Blood'),
        ('NA', 'NA'),
    ], string="Exudate Type")
    offensive_odour = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('NA', 'NA'),
    ], string="Offensive Odour")
    surrounding_skin = fields.Selection([
        ('Dry and Intact', 'Dry and Intact'),
        ('Excoriation', 'Excoriation'),
        ('Redness', 'Redness'),
        ('Blisters', 'Blisters'),
        ('Hypergranulation', 'Hypergranulation'),
        ('Edematous', 'Edematous'),
        ('Indurated', 'Indurated'),
        ('Hematoma', 'Hematoma'),
        ('skin_lesions', 'Skin lesion/s'),
        ('maceration', 'Maceration'),
        ('NA', 'NA'),
    ], string="Surrounding Skin")

    # Measurement:
    Measurement_length = fields.Float(string="Length (cm)")
    Measurement_width = fields.Float(string="Width (cm)")
    Measurement_depth = fields.Float(string="Depth (cm)")
    Measurement_undermining_area = fields.Float(string="*Undermining area (cm)")
    measurement_other = fields.Char(string="Others")
    # Dressing Plan
    dressing_plan_show = fields.Boolean()
    location_wound = fields.Char(string="Location of wound")
    dressing_frequency = fields.Selection([
        ('Daily', 'Daily'),
        ('2 times per week', '2 times per week'),
        ('3 times per week', '3 times per week'),
        ('Weekly', 'Weekly'),
    ], string="Dressing Frequency")
    periwound_skin_care = fields.Selection([
        ('Cavilon Spray', 'Cavilon Spray'),
        ('Cavilon Wipes', 'Cavilon Wipes'),
        ('Duoderm Thin', 'Duoderm Thin'),
        ('VAC Drape', 'VAC Drape'),
        ('NA', 'NA'),
        ('others', 'Others'),
    ], string="Periwound Skin Care")
    periwound_care_other = fields.Char(string="Others")
    clean_irrigate = fields.Selection([
        ('Normal Saline', 'Normal Saline'),
        ('Chlorhexidine', 'Chlorhexidine'),
        ('Betadine', 'Betadine'),
        ('Sterile Water', 'Sterile Water'),
        ('Ulcer Wipes', 'Ulcer Wipes'),
        ('others', 'Others'),
    ], string="Clean / Irrigate with")
    clean_irrigate_other = fields.Char(string="Others")
    primary_dressing = fields.Selection([
        ('hydrogel', 'Hydrogel'),
        ('calcium_alginate_dress', 'Calcium alginate dressing '),
        ('hydrofibre', 'Hydrofibre'),
        ('foam_dressing', 'Foam dressing'),
        ('hypertonic_saline', 'Hypertonic saline'),
        ('povidone_packing', 'Povidone packing/dressing '),
        ('ointment_cream', 'Ointment/Cream:as prescribed'),
        ('paraffin_gauze_dressing', 'Paraffin gauze dressing (preven)'),
        ('NA', 'NA'),
        ('NIL', 'NIL'),
        ('others', 'Others'),
    ], string="Primary Dressing")
    primary_dress_other = fields.Char(string="Others")
    secondary_dressing = fields.Selection([
        ('Absorbent pad', 'Absorbent pad'),
        ('Adhesive Dressing', 'Adhesive Dressing'),
        ('Foam dressing', 'Foam dressing'),
        ('Tegaderm', 'Tegaderm'),
        ('Mepilex', 'Mepilex'),
        ('Mepilex Ag', 'Mepilex Ag'),
        ('NA', 'NA'),
        ('NIL', 'NIL'),
        ('others', 'Others'),
        ], string="Secondary Dressing")
    secondary_dress_other = fields.Char(string="Others")
    secure_with = fields.Selection([
        ('Mefix', 'Mefix'),
        ('Micropore Tape', 'Micropore Tape'),
        ('Tegaderm', 'Tegaderm'),
        ('Crepe Bandage', 'Crepe Bandage'),
        ('Soft Bandage', 'Soft Bandage'),
        ('Stockinette', 'Stockinette'),
        ('Compression Dressing', 'Compression Dressing'),
        ('Tubigrip', 'Tubigrip'),
        ('NA', 'NA'),
        ('others', 'Others'),
        ], string="Secure with")
    secure_other = fields.Char(string="Others")
    for_pressure_ulcer = fields.Selection([
        ('Stage 1', 'Stage 1'),
        ('Stage 2', 'Stage 2'),
        ('Stage 3', 'Stage 3'),
        ('Stage 4', 'Stage 4'),
        ('SDTl', 'SDTl'),
        ('Incontinence Related Dermatitis', 'Incontinence Related Dermatitis'),
        ('surgical_wound', 'Surgical wound'),
        ('NA', 'NA'),
        ('Others', 'Others'),
    ], string="For Pressure Ulcer")
    pressure_ulcer_other = fields.Char(string="Others")
    negative_pressure_wound_vac = fields.Boolean()
    foam_colour = fields.Selection([
        ('NA', 'NA'),
        ('Black', 'Black'),
        ('White', 'White'),
        ('Silver', 'Silver'),
        ('Black and White', 'Black and White'),
        ], string='Foam Colour')
    number_foam = fields.Integer(string="Number of Foam")
    pressure = fields.Selection([
        ('Continuous', 'Continuous'),
        ('Intermittent', 'Intermittent'),
        ('NA', 'NA'),
        ], string="Pressure", default="Intermittent")
    pressure_pump_setting = fields.Selection([
        ('125 mmHg', '125 mmHg'),
        ('150 mmHg', '150 mmHg'),
        ('100 mmHg', '100 mmHg'),
        ('NA', 'NA'),
        ], string="Pressure")
    canister_changed = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('NA', 'NA'),
        ], string="Canister Changed")
    event_recorder = fields.Boolean(string="Any event recorder")
    event_recorder_content = fields.Text()
    present_infection = fields.Boolean(string="Present of Infection")
    present_infection_content = fields.Text()
    surgical_clips = fields.Boolean(string="Surgical Clips or Stitches Remove")
    surgical_clips_content = fields.Text()
    image_show = fields.Boolean()
    image_dressing = fields.Binary()
    wound_assessment_remarks_show = fields.Boolean()
    wound_assessment_remarks_text = fields.Text()

    wound_number_id = fields.Many2one('sm.shifa.wound.assessment', string='Wound Assessment',
                                      ondelete='cascade')

    @api.onchange('number_foam')
    def _check_vital_signs(self):
        if self.number_foam > 100:
            raise ValidationError("invalid Number of Foam")

