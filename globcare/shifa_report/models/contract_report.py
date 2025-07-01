from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


class MonthlyContractSummary(models.Model):
    _name = "monthly.contract.summary"
    _description = "Monthly Summary of Contracts"
    _auto = False  # SQL view based model

    month = fields.Char(string="Month")
    month_start = fields.Date(string="Month Start")
    new_contracts = fields.Integer(string="New Contracts")
    patient_count = fields.Integer(string="Patient Count")
    terminated_contracts = fields.Integer(string="Terminated Contracts")
    active_caregivers = fields.Integer(string="Active Caregivers")

    @api.model
    def init(self):
        self.env.cr.execute("""
            DROP VIEW IF EXISTS monthly_contract_summary;
            CREATE VIEW monthly_contract_summary AS (
                WITH base_months AS (
                    SELECT DATE_TRUNC('month', date) AS month_start FROM sm_caregiver_contracts
                    UNION
                    SELECT DATE_TRUNC('month', write_date) AS month_start FROM sm_caregiver_contracts WHERE state = 'terminated'
                    UNION
                    SELECT DATE_TRUNC('month', create_date) AS month_start FROM oeh_medical_physician
                ),
                aggregated AS (
                    SELECT
                        TO_CHAR(b.month_start, 'YYYY-MM') AS month,
                        b.month_start,

                        -- New contracts
                        (
                            SELECT COUNT(*)
                            FROM sm_caregiver_contracts nc
                            WHERE DATE_TRUNC('month', nc.date) = b.month_start and nc.active = True
                              AND nc.state IN ('active', 'paid', 'evaluation', 'assign_caregiver')
                              AND NOT EXISTS (
                                  SELECT 1 FROM sm_caregiver_contracts c2
                                  WHERE c2.patient_id = nc.patient_id
                                    AND c2.active = True
                                    AND c2.date < nc.date
                                    AND c2.state IN (
                                        'complete', 'cancel', 'hod', 'holdreq', 'terminationreq',
                                        'reactivation_request', 'renew', 'paid', 'terminated',
                                        'completed', 'evaluation', 'assign_caregiver'
                                    )
                              )
                        ) AS new_contracts,

                        -- Patient count
                        (
                            SELECT COUNT(DISTINCT nc.patient_id)
                            FROM sm_caregiver_contracts nc
                            WHERE DATE_TRUNC('month', nc.date) = b.month_start and nc.active = True
                              AND nc.state IN ('active', 'paid', 'evaluation', 'assign_caregiver') 
                              AND NOT EXISTS (
                                  SELECT 1 FROM sm_caregiver_contracts c2
                                  WHERE c2.patient_id = nc.patient_id and c2.active = True
                                    AND c2.date < nc.date
                                    AND c2.state IN (
                                        'complete', 'cancel', 'hod', 'holdreq', 'terminationreq',
                                        'reactivation_request', 'renew', 'paid', 'terminated',
                                        'completed', 'evaluation', 'assign_caregiver'
                                    )
                              )
                        ) AS patient_count,

                        -- Terminated contracts
                        (
                            SELECT COUNT(*)
                            FROM sm_caregiver_contracts t
                            WHERE t.state = 'terminated' and t.active = True
                              AND DATE_TRUNC('month', t.write_date) = b.month_start
                        ) AS terminated_contracts,

                        -- Active caregivers by end of the month
                        (
                            SELECT COUNT(*)
                            FROM oeh_medical_physician p
                            WHERE p.state = 'active'
                              AND p.role_type = 'C'
                              AND p.create_date <= (b.month_start + INTERVAL '1 month - 1 day')
                        ) AS active_caregivers

                    FROM base_months b
                    GROUP BY b.month_start
                )
                SELECT
                    ROW_NUMBER() OVER (ORDER BY month_start) AS id,
                    *
                FROM aggregated
            );
        """)

    def action_view_contracts(self):
        self.ensure_one()
        start_date = self.month_start
        end_date = (start_date + relativedelta(months=1)) - timedelta(days=1)
        self.env.cr.execute("""
            SELECT c.id
            FROM sm_caregiver_contracts c
            WHERE c.date >= %s AND c.date <= %s
              AND c.state IN ('active', 'paid', 'evaluation', 'assign_caregiver')
              AND NOT EXISTS (
                  SELECT 1 FROM sm_caregiver_contracts c2
                  WHERE c2.patient_id = c.patient_id
                    AND c2.date < c.date
                    AND c2.state IN (
                        'complete', 'cancel', 'hod', 'holdreq', 'terminationreq',
                        'reactivation_request', 'renew', 'paid', 'terminated',
                        'completed', 'evaluation', 'assign_caregiver'
                    )
              )
        """, (start_date, end_date))
        contract_ids = [row[0] for row in self.env.cr.fetchall()]
        return {
            'type': 'ir.actions.act_window',
            'name': f"New Contracts in {self.month}",
            'res_model': 'sm.caregiver.contracts',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', contract_ids)],
        }

    def action_view_terminated_contracts(self):
        self.ensure_one()
        start_date = self.month_start
        end_date = (start_date + relativedelta(months=1)) - timedelta(days=1)
        self.env.cr.execute("""
            SELECT c.id
            FROM sm_caregiver_contracts c
            WHERE c.state = 'terminated' 
              AND c.write_date >= %s AND c.write_date <= %s
        """, (start_date, end_date))
        contract_ids = [row[0] for row in self.env.cr.fetchall()]
        return {
            'type': 'ir.actions.act_window',
            'name': f"Terminated Contracts in {self.month}",
            'res_model': 'sm.caregiver.contracts',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', contract_ids)],
        }

    def action_view_active_caregivers(self):
        print("Hello, world!")
        # self.ensure_one()
        # end_date = (self.month_start + relativedelta(months=1)) - timedelta(days=1)
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': f"Active Caregivers in {self.month}",
        #     'res_model': 'oeh.medical.physician',
        #     'view_mode': 'tree,form',
        #     'domain': [
        #         ('state', '=', 'active'),
        #         ('role_type', '=', 'C'),
        #         # ('create_date', '<=', end_date)
        #     ],
        # }
