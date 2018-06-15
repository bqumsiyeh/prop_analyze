import argparse

from prop_analyze.parsers.redfin import RFPropertyScraper, RFListingScraper
from prop_analyze.utils import log, float_to_curr, float_to_percent
from prop_analyze.analysis.parameters import all_params
from prop_analyze.analysis.analyze import Analysis
from prop_analyze.spreadsheet.xls import output_to_xls


def analyze_property(args):

    url = args.url

    # Create Redfin Scraper for this URL
    rf_parser = RFPropertyScraper(url)

    # Scrape and convert to Property with the scraped data from Redfin
    log(f'Scraping {url}')
    result = rf_parser.parse()

    # Check the results of the parsing
    if result.has_issues():
        log(f'{len(result.errors)} errors and {len(result.warnings)} warnings found:')
        for e in result.errors:
            log(f'\tERROR: {e}')
        for w in result.warnings:
            log(f'\tWARNING: {w}')
        log('')

        # If there is at least one critical error, bail out
        if len(result.errors):
            log('Can not continue.  Exiting...')
            return

    prop = result.property

    if args.xls:
        output_to_xls(prop)
    else:
        # Start an analysis
        log(f'Analyzing property...')
        analysis = Analysis(prop)
        res = analysis.anaylze()

        # TODO pretty print
        print(res.to_json())


def find_best(args):
    url = args.url

    rf_parser = RFListingScraper(url)

    log(f'Parsing listings at {url}')
    all_results = rf_parser.parse_listings()

    # Use only the results that parsed without critical errors
    good_results = [r for r in all_results if len(r.errors) == 0]

    log(f'Parsed {len(all_results)} total properties.  {len(good_results)} properties had no errors')

    log(f'Analysing {len(good_results)} properties.')
    analyses = []
    for r in good_results:
        analyses.append(Analysis(r.property).anaylze())

    m = args.count
    log(f'Finding {m} best')

    # TODO sort by AnalysisResult.cash_flow_per_unit OR AnalysisResult.cocr
    analyses.sort(key=lambda r: r.cash_flow_per_unit, reverse=True)
    best = analyses[:m]

    log(f'********************************')
    log(f'{m} best properties - by cash flow per unit')
    log(f'********************************')

    for i in range(len(best)):
        res = best[i]
        p = res.property
        log(f'{i+1}. {p.display_name}\n'
            f'\t{p.url}\n'
            f'\tNumber Of Units: {p.num_units}\n'
            f'\tAsking Price: {float_to_curr(p.price)}\n'
            f'\tCash Flow Per Unit: {float_to_curr(res.cash_flow_per_unit)}\n'
            f'\tCOCR: {float_to_percent(res.cocr)}\n')


def list_params(args):
    log('All Parameters')
    log('****************')
    [log(p.help_text()) for p in all_params]


def main():
    parser = argparse.ArgumentParser(description='Analayzes a property on Redfin and outputs the results')

    subparsers = parser.add_subparsers(help='sub-command help')

    params_parser = subparsers.add_parser('params', help='List all the configurable parameters')
    params_parser.set_defaults(func=list_params)

    analyze_parser = subparsers.add_parser('analyze', help='Analyze a Redfin property')
    analyze_parser.add_argument('url', help='A valid Redfin URL for a property/listing')
    analyze_parser.add_argument('--xls', action='store_true', help='Output analysis to XLS spreadsheet')
    # TODO support parameter value overrides as args
    # for p in all_params:
    #     analyze_parser.add_argument(f'--{p.key}', type=p.val_type, help=p.description)
    analyze_parser.set_defaults(func=analyze_property)

    find_best_parser = subparsers.add_parser('find_best', help='Given a Redfin listing URL, find the best properties')
    find_best_parser.add_argument('url', help='A valid Redfin URL for a property/listing')
    find_best_parser.add_argument('--count', type=int, default=10, help='The number of "best" properties to return')
    find_best_parser.set_defaults(func=find_best)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
