import requests
import re
import json
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from prop_analyze.utils import log, curr_str_to_float
from prop_analyze.property import Property, Utilities

RF_BASE_URL = 'https://www.redfin.com'
RF_ITEM_PROP = 'itemprop'
MAX_LISTINGS = 3000

class RFScrapeResult:
    property: Property

    # Critical errors that stop us from parsing/analysing
    errors: [str]

    # Non-critical warnings that shouldn't stop parsing/analysing
    warnings: [str]

    def __init__(self):
        self.errors = []
        self.warnings = []

    def add_error(self, e: str):
        self.errors.append(e)

    def add_warning(self, w: str):
        self.warnings.append(w)

    def has_issues(self):
        return len(self.errors) or len(self.warnings)


class RFScraper:

    user_agent: str = None
    url: str = None
    page_txt: str = None
    soup = None
    res: RFScrapeResult = None

    def __init__(self, rf_url: str):
        self.url = rf_url

        # Get a fake user agent
        ua = UserAgent()
        # ua.update() TODO figure out why this times out
        self.user_agent = ua.random

    def _validate(self):
        """
        Ensure that this parser can do its job
        :return: boolean
        """
        if not self.url.startswith(RF_BASE_URL):
            self.res.add_error(f'URL must start with {RF_BASE_URL}')
            return False
        return True

    def _make_request(self, url):
        """
        Makes a GET request to a Redfin URL
        :param url: The URL to request
        :return: Request Response
        """

        headers = {'user-agent': self.user_agent}
        r = requests.get(url, headers=headers)

        if r.status_code == 200:
            return r
        elif r.status_code == 503:
            self.res.add_error('Redfin is currently down for maintenance.')
        else:
            self.res.add_error(f'Received a {r.status_code} error code requesting Redfin URL {url}')
        return None


class RFPropertyScraper(RFScraper):

    extra_data: str
    property: Property = None

    @staticmethod
    def _sanitize_value(val):
        """
        Sanitize the value scraped from Redfin before storing it on the Property
        :param val: The value to santize
        :return: The sanitized value
        """
        if isinstance(val, str):
            return val.strip().strip(',')
        else:
            return val

    def _get_extra_data(self):
        """
        In order to get their "below the fold" data to get some things we need, we need to make another request
        to one of their APIs. The query parameters for this API are embedded in the HTML somewhere.
        :return: boolean representing if the operation succeeded
        """

        def _parse_out_val(v: str):
            a = re.findall(f'\"{v}\":\d+', self.page_txt)
            if a and len(a) > 0:
                b = a[0].split(':')
                if b and len(b) > 1:
                    return b[1]
            return None

        # We need the propertyId, accessLevel, and listingId, so parse those out
        property_id = _parse_out_val('propertyId')
        access_level = _parse_out_val('accessLevel')
        listing_id = _parse_out_val('listingId')

        if not property_id or not access_level or not listing_id:
            return False

        # Construct the URL to their API
        extra_data_url = f'https://www.redfin.com/stingray/api/home/details/belowTheFold?' \
                         f'propertyId={property_id}&accessLevel={access_level}&listingId={listing_id}'

        # Make the request
        r = self._make_request(extra_data_url)

        if not r:
            return False

        res_text = r.text

        # For some reason, Redfin prefixes JSON data with {}&&, so strip that out
        prefix = '{}&&'
        if res_text.startswith(prefix):
            res_text = res_text[len(prefix):]

        # Now we should have just JSON left, so load it up.  The interesting part is in 'payload' key.
        inner_data = json.loads(res_text)
        self.extra_data = inner_data['payload']
        return True

    def _get_amenity_from_extra_data(self, group_ref_name: str, amenity_ref_name: str):
        """
        Utility method that parses out the value of a "amenity" from the extra_data
        :param group_ref_name: The 'referenceName' of the group that the amenity is in
        :param amenity_ref_name:  The 'referenceName' of the amenityEntry in the group
        :return: The amenityValues for the given parameters.  This looks like its usually a list
        """
        super_groups = self.extra_data['amenitiesInfo']['superGroups']
        for sg_dict in super_groups:
            amenity_groups = sg_dict['amenityGroups']
            for ag_dict in amenity_groups:
                if ag_dict['referenceName'] == group_ref_name:
                    entries = ag_dict['amenityEntries']
                    for entry in entries:
                        if entry['referenceName'] == amenity_ref_name:
                            return entry['amenityValues']

        # If we get here that means we found nothing
        return None

    def _parse_street_address(self):
        """
        Parse out the street address from the HTML and set it on the property
        :return:
        """
        v = self.soup.find('span', attrs={RF_ITEM_PROP: 'streetAddress'})
        t = v.get_text() if v else ''
        self.property.street_address = self._sanitize_value(t)

    def _parse_city(self):
        """
        Parse out the city from the HTML and set it on the property
        :return:
        """
        v = self.soup.find('span', attrs={RF_ITEM_PROP: 'addressLocality'})
        t = v.get_text() if v else ''
        self.property.city = self._sanitize_value(t)

    def _parse_state(self):
        """
        Parse out the state from the HTML and set it on the property
        :return:
        """
        v = self.soup.find('span', attrs={RF_ITEM_PROP: 'addressRegion'})
        t = v.get_text() if v else ''
        self.property.state = self._sanitize_value(t)

    def _parse_price(self):
        """
        Parse out the purchase price from the HTML and set it on the property
        :return:
        """
        el = self.soup.find('div', attrs={'class': 'info-block price'})
        if el and el.find('div'):
            price_text = el.find('div').get_text()
            price_float = curr_str_to_float(price_text)
            self.property.price = self._sanitize_value(price_float)
        else:
            self.property.price = 0.0
            self.res.add_error('Could not find Price')

    def _parse_num_units(self):
        """
        Parse out the number of units from the extra data and set it on the property
        :return:
        """
        values = None
        combos = [
            ('BuildingInformation', 'TNU'),
            ('Multi-FamilyInformation', 'UNT'),
            ('Multi-FamilyFeatures', 'INCPTUNL')
        ]

        for combo in combos:
            values = self._get_amenity_from_extra_data(combo[0], combo[1])
            if values:
                break

        if values:
            self.property.num_units = int(values[0])
        else:
            # This property is required, so bail out if we cant find it
            self.res.add_error('Could not find # of Units')

    def _parse_total_rent(self):
        """
        Parse out the rent per unit, and sum it up to get the total rent, and set it on the property
        :return:
        """

        total_rent = 0.0
        units_accounted_for = 0
        i = 0

        while i < self.property.num_units and units_accounted_for < self.property.num_units:
            rent_found = False

            unit_rent_arr = None
            combos = [
                (f'Unit{i+1}Information', f'RT{i+1}'),
                (f'Unit{i+1}Information', f'IN{i+1}'),
                (f'Unit{i+1}Information', f'INCPU{i+1}_RT')
            ]

            for combo in combos:
                unit_rent_arr = self._get_amenity_from_extra_data(combo[0], combo[1])
                if unit_rent_arr:
                    break

            if unit_rent_arr:
                try:
                    # Get the rent for this "unit".  This could represent multiple units
                    unit_rent_float = (curr_str_to_float(unit_rent_arr[0]))

                    # Get the number of units this rent accounts for
                    units_of_this_type_arr = self._get_amenity_from_extra_data(f'Unit{i+1}Information', f'AT{i+1}')
                    units_of_this_type = int(units_of_this_type_arr[0]) if units_of_this_type_arr else 1

                    # Add to the total rent taking into account of the number of units of this type
                    total_rent += (unit_rent_float * units_of_this_type)

                    # Update the number of units we have accounted for
                    units_accounted_for += units_of_this_type

                    rent_found = True
                except ValueError:
                    pass

            if not rent_found:
                # Add a warning here, not an error, because we can still consider partial rent when analyzing
                self.res.add_warning(f'Could not find rent for Unit {i+1}')
                break

            i += 1

        self.property.total_rent = total_rent

    def _parse_taxes(self):
        """
        Parse out the tax info from the extra data and set it on the property
        :return:
        """
        try:
            tax_info = self.extra_data['publicRecordsInfo']['taxInfo']
            self.property.tax_year = self._sanitize_value(tax_info['rollYear'])
            self.property.annual_taxes = self._sanitize_value(float(tax_info['taxesDue']))
        except Exception as e:
            self.res.add_error(f'Could not parse out taxes: {e}')

    def _parse_utilities_paid(self):
        """
        Parse out utilities paid by the tenant, per unit, and set it on the property
        :return:
        """
        utilities_paid = []

        # TODO: this doesnt work for all properties.  It works for Chicago properties but not Bay Area properties
        # TODO: Bay area properties use a value called "Tenant Expenses:" which is the inverse. Support that eventually

        util_val_map = {
            'Tenant Pays Electric': Utilities.ELECTRIC,
            'Tenant Pays Gas': Utilities.GAS,
            'Tenant Pays Water': Utilities.WATER
        }
        for i in range(self.property.num_units):
            tenant_pays = self._get_amenity_from_extra_data(f'Unit{i+1}Information', f'TP{i+1}')

            if not tenant_pays:
                # If not found, assume tenant pays all
                utilities_paid.append(Utilities.all())
            else:
                if 'Tenant Pays All' in tenant_pays:
                    utilities_paid.append(Utilities.all())
                    continue

                tenant_utils = []
                for val in tenant_pays:
                    if val in util_val_map:
                        tenant_utils.append(util_val_map[val])
                    else:
                        self.res.add_warning(f'Unknown Tenant Pays value: {val}')
                utilities_paid.append(tenant_utils)

        self.property.utilities_paid_by_unit = utilities_paid

    def _do_parse(self):

        # Parse the page text with BeautifulSoup
        self.soup = BeautifulSoup(self.page_txt, 'html.parser')

        # Get the extra "below the fold" data
        if not self._get_extra_data():
            # If this failed, no point in continuing
            return

        # Start parsing out the things we care about
        self._parse_street_address()
        self._parse_city()
        self._parse_state()
        self._parse_price()
        self._parse_num_units()
        self._parse_total_rent()
        self._parse_taxes()
        self._parse_utilities_paid()

    def parse(self) -> RFScrapeResult:

        # Create result and property
        self.res = RFScrapeResult()
        self.property = Property()
        self.property.url = self.url
        self.res.property = self.property

        # Validate first
        if not self._validate():
            return self.res

        # Request the page at the URL provided
        response = self._make_request(self.url)

        # Make sure we got a valid response
        if not response:
            return self.res

        # Grab the page response
        self.page_txt = response.text

        # Parse it into a Property and return
        self._do_parse()
        return self.res


class RFListingScraper(RFScraper):

    property_urls: [str] = []
    results: [RFScrapeResult] = []

    def _extract_properties(self):

        # Dig out the API url that gives us all of the Listings
        api_url = re.findall('\\\\u002Fstingray\\\\u002Fapi\\\\u002Fgis\?.*?(?=\")', self.page_txt)[0]
        api_url = api_url.encode('utf-8').decode('unicode_escape')
        api_url = re.sub('num_homes=\d+', f'num_homes={MAX_LISTINGS}', api_url)
        api_url = f'{RF_BASE_URL}{api_url}'

        # Make the request
        r = self._make_request(api_url)
        res_text = r.text

        # For some reason, Redfin prefixes JSON data with {}&&, so strip that out
        prefix = '{}&&'
        if res_text.startswith(prefix):
            res_text = res_text[len(prefix):]

        # Now we should have just JSON left, so load it up.  The interesting part is in 'payload' key.
        inner_data = json.loads(res_text)
        homes = inner_data['payload']['homes']

        for h in homes:
            prop_url = h['url']
            self.property_urls.append(f'{RF_BASE_URL}{prop_url}')

    def _parse_properties(self):
        for url in self.property_urls:
            scraper = RFPropertyScraper(url)
            self.results.append(scraper.parse())

            if len(self.results) % 10 == 0:
                log(f'Parsed {len(self.results)} out of {len(self.property_urls)} properties')

    def parse_listings(self) -> [RFScrapeResult]:

        # Validate first
        self._validate()

        # Request the page at the URL provided
        response = self._make_request(self.url)
        self.page_txt = response.text

        # Extract the property URLs from the listings
        self._extract_properties()
        log(f'Found {len(self.property_urls)} total properties')

        # Scape all the properties individually
        self._parse_properties()

        # Return the results
        return self.results



