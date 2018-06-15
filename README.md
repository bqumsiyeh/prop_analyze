# prop_analyze
Script that parses property listings (on Redfin) and analyzes them.

This script currently has 2 sets of options:
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
This subcommand will accept a Redfin Listings URL (from the map view), parse out all of the properties, analyze them 
and find the best ones, ranked by Cash Flow per Unit

Example:
```python
python prop_analyze.py find_best find_best https://www.redfin.com/city/29470/IL/Chicago/filter/property-type=multifamily,min-beds=6,viewport=42.02460124307162:41.642287205421944:-87.52216567894638:-87.9420716694246
```
Options:
Options:
- `--count`: An integer specifying how many to return.  Defaults to 10 (which means it will return the 10 best properties)