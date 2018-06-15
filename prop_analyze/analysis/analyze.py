from prop_analyze.property import Property
from prop_analyze.analysis.parameters import get_variables_for_property
from prop_analyze.analysis.result import AnalysisResult


class Analysis:

    # The property to analyze
    property: Property

    # All of the available params
    params: dict

    # All of the variables needed to analyze
    variables: dict
    
    def __init__(self, p: Property):
        self.property = p

        # Collect the variables / parameters for this property
        self.variables = get_variables_for_property(self.property)

    def anaylze(self) -> AnalysisResult:

        price = self.property.price
        rent = self.property.total_rent
        taxes = self.property.annual_taxes
        num_units = self.property.num_units
        v_down_payment = self.variables['down_payment']
        v_closing_costs = self.variables['closing_costs']
        v_renovation = self.variables['renovation_budget']
        v_loan_points = self.variables['loan_points']
        v_other_income = self.variables['other_income']
        v_interest_rate = self.variables['interest_rate']
        v_loan_years = self.variables['loan_years']
        v_electricity = self.variables['electricity_expense']
        v_gas = self.variables['gas_expense']
        v_water = self.variables['water_expense']
        v_sewer = self.variables['sewer_expense']
        v_garbage = self.variables['garbage_expense']
        v_hoa = self.variables['hoa_expense']
        v_insurance = self.variables['insurance_expense']
        v_other_expenses = self.variables['other_expense']
        v_vacancy = self.variables['vacancy']
        v_repairs = self.variables['repairs']
        v_capex = self.variables['capex']
        v_prop_mgmt = self.variables['prop_mgmt']

        res = AnalysisResult()
        res.property = self.property

        # Loan Amount
        res.loan_amount = price * (1 - v_down_payment)

        # Total Cash Needed
        res.total_cash_needed = v_closing_costs + v_renovation + \
                                (price * v_down_payment) + \
                                (res.loan_amount * v_loan_points)

        # Gross Income
        res.gross_income = rent + v_other_income

        # P&I
        res.monthly_p_and_i = ((v_interest_rate / 12) * res.loan_amount) / \
                              (1 - (1 + (v_interest_rate / 12)) ** (-12 * v_loan_years))

        # Total Operating Expenses
        res.monthly_total_operating_expenses = (v_electricity + v_gas + v_water + v_sewer + v_garbage + v_hoa) + \
                                               (v_insurance / 12) + \
                                               (taxes / 12) + \
                                               v_other_expenses + \
                                               (rent * v_vacancy) + \
                                               (rent * v_repairs) + \
                                               (rent * v_capex) + \
                                               (rent * v_prop_mgmt)

        # NOI
        res.net_operating_income = res.gross_income - res.monthly_total_operating_expenses

        # Cash Flow
        res.total_cash_flow = res.net_operating_income - res.monthly_p_and_i

        # Cash Flow Per Unit
        res.cash_flow_per_unit = res.total_cash_flow / num_units

        # Cap Rate
        res.cap_rate = (res.net_operating_income * 12) / res.loan_amount

        # Loan Constant
        res.loan_constant = (res.monthly_p_and_i * 12) / res.loan_amount

        # COCR
        res.cocr = (res.total_cash_flow * 12) / res.total_cash_needed

        # Debt Coverage
        res.debt_coverage = res.net_operating_income / res.monthly_p_and_i

        return res
