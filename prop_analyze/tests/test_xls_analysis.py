from openpyxl import load_workbook
import unittest
from prop_analyze.property import Property, Utilities
from prop_analyze.spreadsheet.xls import output_to_xls
from prop_analyze.analysis.analyze import Analysis


class TestXlsMatchesAnalysis(unittest.TestCase):

    @staticmethod
    def _create_property(name: str,
                         price: float,
                         num_units: int,
                         total_rent: float,
                         taxes: float) -> Property:
        p = Property()
        p.url = p.street_address = p.city = p.state = name
        p.price = price
        p.num_units = num_units
        p.total_rent = total_rent
        p.annual_taxes = taxes
        p.utilities_paid_by_unit = [Utilities.all() for u in range(num_units)]
        return p

    def _compare(self, prop: Property):

        # Run out analysis on it
        analysis = Analysis(prop)
        res = analysis.anaylze()

        # Convert it to XLS
        outfile = output_to_xls(prop)

        # Open the XLS file we just created
        wb = load_workbook(filename=outfile, data_only=True)
        sheet = wb.worksheets[0]

        map = {
            'B6': res.loan_amount,
            'B10': res.total_cash_needed
        }

        # TODO this doesnt work because openpyxl doesnt calculate the formula
        for k in map:
            self.assertEqual(sheet[k].value, map[k])

    def test_xls_matches_analysis(self):
        a = self._create_property('a', 100000, 3, 2000, 3000)
        self._compare(a)
