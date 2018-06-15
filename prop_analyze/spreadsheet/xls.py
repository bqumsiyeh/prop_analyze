from openpyxl import load_workbook
from prop_analyze.property import Property
from prop_analyze.analysis.parameters import get_variables_for_property
from prop_analyze.utils import log
import os


def output_to_xls(prop: Property) -> str:

    path = os.path.dirname(os.path.realpath(__file__))
    infile = f'{path}/analysis_template_v1.xlsx'
    outfile = f'{path}/{prop.display_name}.xlsx'

    # Get the variables / parameters for this property
    variables = get_variables_for_property(prop)

    price = prop.price
    rent = prop.total_rent
    taxes = prop.annual_taxes
    num_units = prop.num_units
    v_down_payment = variables['down_payment']
    v_closing_costs = variables['closing_costs']
    v_renovation = variables['renovation_budget']
    v_loan_points = variables['loan_points']
    v_other_income = variables['other_income']
    v_interest_rate = variables['interest_rate']
    v_loan_years = variables['loan_years']
    v_electricity = variables['electricity_expense']
    v_gas = variables['gas_expense']
    v_water = variables['water_expense']
    v_sewer = variables['sewer_expense']
    v_garbage = variables['garbage_expense']
    v_hoa = variables['hoa_expense']
    v_insurance = variables['insurance_expense']
    v_other_expenses = variables['other_expense']
    v_vacancy = variables['vacancy']
    v_repairs = variables['repairs']
    v_capex = variables['capex']
    v_prop_mgmt = variables['prop_mgmt']

    # Open the template
    wb = load_workbook(filename=infile)
    sheet = wb.worksheets[0]

    # Asking Price
    sheet['B1'] = price
    # Closing Costs
    sheet['B2'] = v_closing_costs
    # Renovation Budget
    sheet['B3'] = v_renovation
    # Down Payment
    sheet['B5'] = v_down_payment
    # Loan Points
    sheet['B7'] = v_loan_points
    # Loan Interest
    sheet['B8'] = v_interest_rate
    # Loan Years
    sheet['B9'] = v_loan_years
    # Number of Units
    sheet['F1'] = num_units
    # Gross Rent
    sheet['F2'] = rent
    # Other Income
    sheet['F3'] = v_other_income
    # Electricity
    sheet['F4'] = v_electricity
    # Gas
    sheet['F5'] = v_gas
    # Water
    sheet['F6'] = v_water
    # Sewer
    sheet['F7'] = v_sewer
    # Garbage
    sheet['F8'] = v_garbage
    # HOA
    sheet['F9'] = v_hoa
    # Insurance
    sheet['F10'] = v_insurance
    # Taxes
    sheet['F11'] = taxes
    # Other Expenses
    sheet['F12'] = v_other_expenses
    # Vacancy
    sheet['F14'] = v_vacancy
    # Repairs and Maintenance
    sheet['F15'] = v_repairs
    # Capex
    sheet['F16'] = v_capex
    # Property Management
    sheet['F17'] = v_prop_mgmt
    # Experiment Max Offer
    sheet['I13'] = price * 0.9  # 90%
    # Redfin URL
    sheet['A22'] = 'Redfin Link'
    sheet['A22'].hyperlink = prop.url

    # Write to file
    wb.save(filename=outfile)
    log(f'Outputted to {outfile}')

    return outfile
