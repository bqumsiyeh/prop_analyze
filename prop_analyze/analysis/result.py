import json
from prop_analyze.property import Property


class AnalysisResult:
    property: Property
    loan_amount: float
    total_cash_needed: float
    gross_income: float
    monthly_p_and_i: float
    monthly_total_operating_expenses: float
    net_operating_income: float
    total_cash_flow: float
    cash_flow_per_unit: float
    cap_rate: float
    loan_constant: float
    cocr: float
    debt_coverage: float

    def to_json(self) -> str:
        return json.dumps(self, indent=4, default=lambda o: o.__dict__)