import csv
import json

import urllib.request
import xmltodict as xml

from termcolor import colored

from utils import load_config


# load the config
ISC_CONFIG = load_config.isc_config().get()


# set defaults
PRODUCT_URL_SUFFIX = (
    '?version=v1&type=xml&dataset=normal,'
    'prices,parentCategories,allImages,attributes'
    )

PRODUCT_BASE_URL = (
    'https://www.ikea.com/{}/'.format(ISC_CONFIG['country_code'])
    + '{}/catalog/products/'.format(ISC_CONFIG['language_code'])
    )

AVAILABILITY_BASE_URL = (
    'https://www.ikea.com/{}'.format(ISC_CONFIG['country_code'])
    + '/{}'.format(ISC_CONFIG['language_code'])
    + '/iows/catalog/availability/'
    )

PRODUCT_INFO = []
PRODUCT_AVAILABILITY = []
NOT_PUBLISHED = []


def get_store_name(store_id):
    '''
    Gets the store name from the store ID

    Inputs:
        store_id int: The store ID

    Returns: The store name
    '''
    for n in ISC_CONFIG['store_names']:
        if n['id'] == store_id:
            return n['name']


def load_input_CSV(in_file):
    '''
    Reads the input CSV file

    Returns: An array of dictionaries
    [{'id': '01234567', 'qty': 1, 'notes':'blah'}]
    '''
    out = []
    with open(in_file) as csvFile:
        reader = csv.reader(csvFile, delimiter=',')

        for count, row in enumerate(reader):
            if count > 0:
                # Process the rows to a dict
                if row[1] == '':
                    qty = 1
                else:
                    qty = int(row[1])
                this_item = {
                    "id": row[0].replace(".", ""),
                    "qty": qty,
                    "notes": row[2]
                }

                out.append(this_item)

    return out


def get_product_info(item_id, verbose):
    '''
    Gets the product color, description, size, and price

    Inputs:
        item_id string: The item id

    Returns: A dict with the product info
        e.g.
        {
            'item_id': '01234567',
            'price': 229.0,
            'color': 'white',
            'description': 'EXAMPLE product',
            'size': '1x1'
         }
    '''

    # If we already got info for this product, return it
    for prod in PRODUCT_INFO:
        if prod['item_id'] == item_id:
            return prod

    url = "{}{}{}".format(PRODUCT_BASE_URL, item_id, PRODUCT_URL_SUFFIX)
    try:
        data = urllib.request.urlopen(url).read()
        data = xml.parse(data)
    except urllib.error.HTTPError as e:
        print('\nError encountered when querying url: {}\n'.format(url))
        print(e)
        # pretty_print(data)

    try:
        item = data['ir:ikea-rest']['products']['product']['items']['item']
        item_info = {}
        item_info['item_id'] = item_id

        # pricing
        item_info['price'] = float(
            item['prices']['normal']['priceNormal']['@unformatted'])

        # description & color
        try:
            item_info['color'] = (
                item['attributesItems']['attributeItem'][0]['value'])
        except:
            item_info['color'] = ''
        item_info['description'] = item['name'] + ' ' + item['facts']

        # size
        try:
            item_info['size'] = (
                item['attributesItems']['attributeItem'][1]['value'])
        except:
            item_info['size'] = ''
        if verbose:
            print(
                '\nRetrived info for product: ',
                item_info['item_id'],
                item_info['description'])

        # Save for later
        PRODUCT_INFO.append(item_info)

        return item_info
    except KeyError as e:
        try:
            error = data['ir:ikea-rest']['products']['error']
            errorcode = error['@code']
            errormsg = error['message']
            print(colored(
                    '\nError: ' + errormsg
                    + ', Code: ' + errorcode
                    + ', Item: ' + item_id,
                    'red'
                    ))
            NOT_PUBLISHED.append(item_id)
            return False
        except:
            print(colored(
                    '\nError: ' + e
                    + ' for product: ' + item_id,
                    'red'
                   ))

        # print(colored('\nQuitting.', 'red'))
        # quit()


def get_product_availability(item_id, verbose):
    '''
    For a specified product ID, gets stock info at the requested stores

    Input:
        item_id string: The item ID

    Returns: a list of dictionaries containing item availability
    '''

    # If we already got availability for this product, return it
    for prod in PRODUCT_AVAILABILITY:
        try:
            if prod[0]['item_id'] == item_id:
                return prod
        except IndexError:
            continue

    url = AVAILABILITY_BASE_URL + item_id
    data = urllib.request.urlopen(url).read()
    data = xml.parse(data)
    availability = data['ir:ikea-rest']['availability']['localStore']
    # pretty_print(availability)

    out = []

    for id in ISC_CONFIG['store_ids']:
        for store in availability:
            if store['@buCode'] == id:
                store_dict = {}
                stock = store['stock']

                # Store ID and name
                store_dict['store_id'] = id
                store_dict['store_name'] = get_store_name(id)

                # basic availability info
                store_dict['item_id'] = item_id
                store_dict['available'] = int(stock['availableStock'])
                if store_dict['available'] == 0:
                    try:
                        store_dict['restockDate'] = stock['restockDate']
                    except KeyError:
                        store_dict['restockDate'] = None
                store_dict['probability'] = stock['inStockProbabilityCode']
                store_dict['isMultiProduct'] = (
                    str_to_bool(stock['isMultiProduct'])
                    )

                # item location(s)
                loc = stock['findItList']['findIt']
                locations = []
                if store_dict['isMultiProduct']:
                    for item in loc:
                        item_dict = get_item_location(item)
                        locations.append(item_dict)
                else:
                    item_dict = get_item_location(loc)
                    locations.append(item_dict)

                store_dict['locations'] = locations

                # forecast
                try:
                    if store_dict['restockDate']:
                        store_dict['forecast'] = stock['forecasts']['forcast']
                    else:
                        store_dict['forecast'] = None
                except KeyError:
                    store_dict['restockDate'] = 'N/A'

                out.append(store_dict)

                # print the status to the terminal
                confcolor = color_confidence(store_dict['probability'])
                print(
                    'At store:', store_dict['store_name'],
                    'Qty:', colored(store_dict['available'], confcolor),
                    'In-Stock Confidence:',
                    colored(store_dict['probability'], confcolor))
                if store_dict['available'] == 0:
                    print('Restock date:', store_dict['restockDate'])
                    if store_dict['forecast']:
                        for f in store_dict['forecast']:
                            confcolor = (
                                color_confidence(f['inStockProbabilityCode'])
                                )
                            print('Forecast:')
                            print(
                                f['validDate'],
                                'Qty:',
                                colored(f['availableStock'], confcolor),
                                'Confidence:',
                                colored(f['inStockProbabilityCode'])
                                )
                    else:
                        print(
                            'Forecast:',
                            colored(
                                'No estimated restock date availabile',
                                confcolor
                                )
                            )

    # Save for later
    PRODUCT_AVAILABILITY.append(out)

    return out


def color_confidence(probability):
    '''
    Assigns Green/Yellow/Red colors to in-stock probability values

    Input: The in-stock probability

    Returns: A color for use by the colored library
    '''
    if probability == 'HIGH':
        return 'green'
    elif probability == 'MEDIUM':
        return 'yellow'
    else:
        return 'red'


def get_item_location(item):
    '''
    Gets an item's location within the store

    Inputs:
        item dict: The dictionary containing the item

    Returns: A dict with the item location
    '''
    item_dict = {}
    item_dict['partNumber'] = item['partNumber']
    item_dict['qty'] = int(item['quantity'])

    if item['type'] == 'BOX_SHELF':
        aisle = item['box']
        bin = item['shelf']
        item_dict['location'] = 'Warehouse ' + aisle + '-' + bin
    elif item['type'] == 'CONTACT_STAFF':
        item_dict['location'] = 'Contact Staff'
    elif item['type'] == 'SPECIALTY_SHOP':
        item_dict['location'] = item['specialtyShop'] + ' Dept.'
    else:
        item_dict['location'] = item['type']

    return item_dict


def str_to_bool(s):
    '''
    Converts a 'true' or 'false' string to boolean

    Input:
        s: The string to convert

    Returns: the boolean value
    '''
    if s == 'true':
        return True
    elif s == 'false':
        return False
    else:
        raise ValueError


def pretty_print(data):
    '''
    Pretty prints dictionaries

    Input:
        data dict: The dictionary to pretty print
    '''
    print(json.dumps(data, indent=1))


def load_parse_all_products(items, verbose):
    '''
    Loads and parses all products

    Returns [dict]: A list of products
    '''

    products = []
    for item in items:
        # Get product info
        product = {}
        product['id'] = item['id']
        product['qty_needed'] = item['qty']
        product['notes'] = item['notes']
        item_info = get_product_info(item['id'], verbose)
        if item_info:
            product['info'] = item_info
            product['availability'] = (
                get_product_availability(item['id'], verbose)
                )
        else:
            product['info'] = "Not available"
            product['availability'] = "Not available"

        products.append(product)

    return products


def calc_total_price(products):
    '''
    Computes the total price of the list

    Inputs:
        products [dict]: The list of products

    Returns float: The total price
    '''
    total_price = 0.0

    for prod in products:
        total_price = total_price + prod['info']['price'] * prod['qty_needed']

    return total_price


def get_stock_confidence(products):
    '''
    Determines the in-stock probability for the entire list by store

    Returns:
        The stock confidence for each store
    '''
    confidence = []
    for store in ISC_CONFIG['store_ids']:
        store_dict = {}
        store_dict['id'] = store
        store_dict['confidence'] = 'HIGH'
        confidence.append(store_dict)

    for prod in products:
        for store in prod['availability']:
            store_id = store['store_id']
            probability = store['probability']

            if probability == 'LOW':
                for store in confidence:
                    if store['id'] == store_id:
                        store['confidence'] = 'LOW'
            elif confidence == 'MEDIUM':
                for store in confidence:
                    if store['id'] == store_id and \
                       store['confidence'] != 'LOW':
                        store['confidence'] = 'MEDIUM'

    return confidence


def save_file(filename, rows):
    '''
    Saves rows (list of lists) as a CSV file

    Inputs:
        filename string: The filename
        rows [[]]: The data to save
    '''
    with open(filename, 'w', newline='') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        for row in rows:
            wr.writerow(row)
    print('\nSaved file', filename)


def save_product_availability(products, verbose):
    '''
    Gets product info and availability and exports to CSV files
    '''
    total_price = calc_total_price(products)
    stock_confidence = get_stock_confidence(products)
    # pretty_print(products)

    for store in ISC_CONFIG['store_ids']:
        rows = []

        total_items = 0
        meets_qty_reqs = True

        store_name = get_store_name(store)
        rows.append(['Store', store_name])
        rows.append(['Store ID', store])
        for con in stock_confidence:
            if con['id'] == store:
                confidence = con['confidence']
                break
        rows.append(['In-Stock Confidence', confidence])
        rows.append(['Total Price', total_price])
        rows.append(['\n'])

        rows.append(
                    [
                        'Part Number',
                        'Description',
                        'Location',
                        'Qty Needed',
                        'Qty Available',
                        'In-Stock Confidence',
                        'Color',
                        'Size',
                        'Unit Price',
                        'Notes'
                    ]
            )

        for prod in products:
            for avail in prod['availability']:
                if avail['store_id'] == store:
                    thisrow = []

                    if not avail['isMultiProduct']:
                        # Not a multi-part product
                        num_items = (
                            avail['locations'][0]['qty'] * prod['qty_needed'])
                        total_items = total_items + num_items

                        notes0 = prod['notes']

                        if prod['qty_needed'] > avail['available']:
                            meets_qty_reqs = False
                            notes0 = 'NOT ENOUGH QTY! ' + prod['notes']

                        thisrow.append(prod['id'])
                        thisrow.append(prod['info']['description'])
                        thisrow.append(avail['locations'][0]['location'])
                        thisrow.append(num_items)
                        thisrow.append(avail['available'])
                        thisrow.append(avail['probability'])
                        thisrow.append(prod['info']['color'])
                        thisrow.append(prod['info']['size'])
                        thisrow.append(prod['info']['price'])
                        thisrow.append(notes0)
                        rows.append(thisrow)
                    else:
                        # Multi-part product

                        notes1 = prod['notes']

                        if prod['qty_needed'] > avail['available']:
                            meets_qty_reqs = False
                            notes1 = 'NOT ENOUGH QTY! ' + prod['notes']

                        thisrow.append(prod['id'])
                        thisrow.append(prod['info']['description'])
                        thisrow.append('Multi-Part Product. See Below:')
                        thisrow.append(prod['qty_needed'])
                        thisrow.append(avail['available'])
                        thisrow.append(avail['probability'])
                        thisrow.append(prod['info']['color'])
                        thisrow.append(prod['info']['size'])
                        thisrow.append(prod['info']['price'])
                        thisrow.append(notes1)
                        rows.append(thisrow)

                        for loc in avail['locations']:
                            num_items = prod['qty_needed']*int(loc['qty'])
                            total_items = total_items + num_items

                            notes2 = 'Part of ' + prod['id']

                            info = get_product_info(loc['partNumber'], verbose)
                            avail = (
                                      get_product_availability(
                                          loc['partNumber'],
                                          verbose
                                        )
                                    )
                            for thisstore in avail:
                                if thisstore['store_id'] == store:
                                    avail = thisstore

                            if num_items > avail['available']:
                                meets_qty_reqs = False
                                notes2 = 'NOT ENOUGH QTY! ' + notes2

                            thisrow = []
                            thisrow.append(loc['partNumber'])
                            thisrow.append(info['description'])
                            thisrow.append(loc['location'])
                            thisrow.append(num_items)
                            thisrow.append(avail['available'])
                            thisrow.append(avail['probability'])
                            thisrow.append(info['color'])
                            thisrow.append(info['size'])
                            thisrow.append(info['price'])
                            thisrow.append(notes2)
                            rows.append(thisrow)

        rows.insert(4, ['Total Items', total_items])
        rows.insert(3, ['Meets Qty Reqs', meets_qty_reqs])

        save_file('out_' + str(store_name) + '.csv', rows)
    if verbose:
        print(colored('\nDone.', 'green'))


def get(items, verbose):
    products = load_parse_all_products(items, verbose)
    # remove items that are no longer available
    for item in NOT_PUBLISHED:
        products = list(filter(lambda i: i['id'] != item, products))
    save_product_availability(products, verbose)


if __name__ == "__main__":
    items = load_input_CSV('../in.csv')
    get(items, verbose=True)
