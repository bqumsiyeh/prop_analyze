# prop_analyze
This is a script that parses property listings (on Redfin) and analyzes them.  This script is targeted for 
analyzing investment properties, with a focus on multi-family apartment buildings.

This script currently has 2 sets of functionalities:
1. Parses and analyzes a Redfin property listing and outputs as JSON or an XLS spreadsheet
2. Parses a Redfin property listings url (with multiple properties), analyzes all of them, and finds the best ones

## Installation
```python
pip install -r requirements.txt
```
## Usage
### Analyze a single property
This subcommand will accept a Redfin property URL, parse out the relevant information, then analyze it.

Example:
```python
python prop_analyze.py analyze https://www.redfin.com/IL/Chicago/7600-S-Green-St-60620/home/13913979
```
Options:
- `--xls`: Output the analysis to a friendly XLS spreadsheet.  If not specified, output will be JSON by default

### Find Best Properties
This subcommand will accept a Redfin Listings URL, parse out all of the properties, analyze all of them 
and print out the best ones, sorted by Cash Flow per Unit.

The listings URL must be of the map view page, and can include any preset filters you have. An example URL can be 
found [here](https://www.redfin.com/city/29470/IL/Chicago/filter/property-type=multifamily,min-beds=6,viewport=42.02460124307162:41.642287205421944:-87.52216567894638:-87.9420716694246)

Example:
```python
python prop_analyze.py find_best https://www.redfin.com/city/29470/IL/Chicago/filter/property-type=multifamily,min-beds=6,viewport=42.02460124307162:41.642287205421944:-87.52216567894638:-87.9420716694246
```
Options:
- `--count`: An integer specifying how many to return.  Defaults to 10 (which means it will return the 10 best properties)

## Configuration
All of the variables used in the analysis calculations can be tweaked to your content.  These can all be found in
 `prop_analyze/analysis/parameters.py`
 
The following variables can be modified:
```
Name                Default     Description
______________________________________________________________________________________________________
interest_rate       0.05        The interest rate of the loan, as a percentage
closing_costs       5000.0      The estimated closing costs
renovation_budget   0.0         The estimated renovation budge
down_payment        0.25        The down payment for the loan, as a percentage
loan_points         0.00125     The loan points, as a percentage
loan_years          30          The number of years that the loan is ammortized over
other_income        0.0         Any other misc income to consider when analyzing
electricity_expense 25.0        The estimated monthly electricity expense, per unit
gas_expense         35.0        The estimated monthly gas expense, per unit
water_expense       35.0        The estimated water electricity expense, per unit
sewer_expense       5.0         The estimated monthly sewer expense, per unit
garbage_expense     5.0         The estimated monthly garbage expense, per unit
hoa_expense         0.0         The estimated monthly total HOA expense
insurance_expense   500.0       The estimated yearly insurance expense, per unit
other_expense       40.0        The total estimated misc expenses
vacancy             0.07        The estimate vacancies factor, as percentage of the monthly rent
repairs             0.05        The estimate repairs rate, as percentage of the monthly rent
capex               0.05        The estimate Capex rate, as percentage of the monthly rent
prop_mgmt           0.1         The estimate Property Management rate, as percentage of the monthly rent

```
