from prop_analyze.property import Property, Utilities


class Parameter:
    key: str
    description: str
    default_val: object
    per_unit: bool = False
    utility_type: Utilities = None

    def help_text(self):
        return f'{self.key}\t{self.default_val}\t{self.description}'


class LoanInterestRate(Parameter):
    key = 'interest_rate'
    description = 'The interest rate of the loan, as a percentage'
    default_val = 0.05


class ClosingCosts(Parameter):
    key = 'closing_costs'
    description = 'The estimated closing costs'
    default_val = 5000.0


class RenovationBudget(Parameter):
    key = 'renovation_budget'
    description = 'The estimated renovation budge'
    default_val = 0.0


class DownPayment(Parameter):
    key = 'down_payment'
    description = 'The down payment for the loan, as a percentage'
    default_val = 0.25


class LoanPoints(Parameter):
    key = 'loan_points'
    description = 'The loan points, as a percentage'
    default_val = 0.00125


class LoanYears(Parameter):
    key = 'loan_years'
    description = 'The number of years that the loan is ammortized over'
    default_val = 30


class OtherIncome(Parameter):
    key = 'other_income'
    description = 'Any other misc income to consider when analyzing'
    default_val = 0.0


class ElectricityExpense(Parameter):
    key = 'electricity_expense'
    description = 'The estimated monthly electricity expense, per unit'
    default_val = 25.0
    per_unit = True
    utility_type = Utilities.ELECTRIC


class GasExpense(Parameter):
    key = 'gas_expense'
    description = 'The estimated monthly gas expense, per unit'
    default_val = 35.0
    per_unit = True
    utility_type = Utilities.GAS


class WaterExpense(Parameter):
    key = 'water_expense'
    description = 'The estimated water electricity expense, per unit'
    default_val = 35.0
    per_unit = True
    utility_type = Utilities.WATER


class SewerExpense(Parameter):
    key = 'sewer_expense'
    description = 'The estimated monthly sewer expense, per unit'
    default_val = 5.0
    per_unit = True
    utility_type = Utilities.SEWER


class GarbageExpense(Parameter):
    key = 'garbage_expense'
    description = 'The estimated monthly garbage expense, per unit'
    default_val = 5.0
    per_unit = True
    utility_type = Utilities.GARBAGE


class HoaExpense(Parameter):
    key = 'hoa_expense'
    description = 'The estimated monthly total HOA expense'
    default_val = 0.0


class InsuranceExpense(Parameter):
    key = 'insurance_expense'
    description = 'The estimated yearly insurance expense, per unit'
    default_val = 500.0
    per_unit = True


class OtherExpenses(Parameter):
    key = 'other_expense'
    description = 'The total estimated misc expenses'
    default_val = 40.0


class Vacancy(Parameter):
    key = 'vacancy'
    description = 'The estimate vacancies factor, as percentage of the monthly rent'
    default_val = 0.07


class RepairsAndMgmt(Parameter):
    key = 'repairs'
    description = 'The estimate repairs rate, as percentage of the monthly rent'
    default_val = 0.05


class Capex(Parameter):
    key = 'capex'
    description = 'The estimate Capex rate, as percentage of the monthly rent'
    default_val = 0.05


class PropManagement(Parameter):
    key = 'prop_mgmt'
    description = 'The estimate Property Management rate, as percentage of the monthly rent'
    default_val = 0.1


all_params = [
    LoanInterestRate(),
    ClosingCosts(),
    RenovationBudget(),
    DownPayment(),
    LoanPoints(),
    LoanYears(),
    OtherIncome(),
    ElectricityExpense(),
    GasExpense(),
    WaterExpense(),
    SewerExpense(),
    GarbageExpense(),
    HoaExpense(),
    InsuranceExpense(),
    OtherExpenses(),
    Vacancy(),
    RepairsAndMgmt(),
    Capex(),
    PropManagement()
]


def get_variables_for_property(prop: Property):

    params = dict((p.key, p) for p in all_params)

    variables = dict()

    # For each variable, use the default value from the param.  If it's per unit, then multiply
    for k, p in params.items():

        if p.utility_type:
            # If this is a utlity, only count it if we know this unit pays utilities
            v = 0.0
            for utilities_for_unit in prop.utilities_paid_by_unit:
                # If this utility is in the list of utilities paid by tenant, dont count it
                if p.utility_type in utilities_for_unit:
                    v += p.default_val

        elif p.per_unit:
            # If per unit, then multiply by number of units
            v = p.default_val * prop.num_units
        else:
            # Otherwise just use the normal value
            v = p.default_val

        variables[k] = v

    return variables
