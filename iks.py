import configparser
import json
import os
import sys

import click

sys.path.insert(0, '/utils/')

from utils import check_stock, stores, home_planner, add_to_list


@click.group()
def main():
    """
    Simple CLI for working with the ikea API
    """
    pass


@main.command()
@click.argument('store_list')
@click.option('--country', 
    default='us',
    help='Target country')
@click.option('--language',
    default='en',
    help='Language')
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
def config(verbose, store_list, country, language):
    """
    Sets the target store(s) to search.
    Accepts a comma separate list of stores.
    Example: iks.py set-stores 119,117
    """
    config = configparser.ConfigParser()
    config['CONFIG'] = {}
    config['CONFIG']['IKEA_COUNTRY_CODE'] = country
    config['CONFIG']['IKEA_LANG_CODE'] = language

    config['SECRET'] = {}
    config['SECRET']['IKEA_SESSION_COOKIE'] = ""
    config['SECRET']['IKEA_LIST_ID'] = ""
    config['SECRET']['IKEA_STORE_ID'] = ""

    formatted_store_list = store_list.split(',')

    valid_stores = []
    complete_store_list = stores.get_ids(loc=country, store_map="stores.json")
    for store in formatted_store_list:
        if store in complete_store_list:
            valid_stores.append(store)

    if not valid_stores:
        if verbose: 
            click.echo('\nERROR stores not found in the provided country: {}.'.format(country))
            click.echo('Please set a country code and try again\n')
    else:
        config['CONFIG']['IKEA_STORES'] = json.dumps(valid_stores)
        if verbose:
            click.echo("\nThe following Env vars have been set \n\n"
                        + "IKEA_COUNTRY_CODE: {}\n".format(country)
                        + "IKEA_LANG_CODE: {}\n".format(language)
                        + "IKEA_STORES: {}\n".format(json.dumps(valid_stores))
            )
    f = open("config.ini", "+w")
    config.write(f)

@main.command()
@click.option('--country',
    default='us',
    help='Required to validate your store code if the store is located outside the US')
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
def get_stores(verbose, country):
    """
    Prints a list of stores for the target country.
    Must be a valid contry code.
    """

    store_map="stores.json"
    country_codes = stores.list_country_codes(store_map)

    if country not in country_codes:
        if verbose: 
            click.echo('\nERROR - country code: {} is not a valid country code.\n'.format(country))
            click.echo('Check your country code by looking at the Ikea URL of your target country')
            click.echo("For example, in the U.S. the URL is https://www.ikea.com/us/en/ and the country code is \'us\'\n")
    else:
        if verbose: 
            click.echo(
                json.dumps(stores.get(loc=country,store_map=store_map),
                indent=4, sort_keys=True))


@main.command()
@click.argument('home_planner_file', type=click.Path(exists=True))
@click.option('--output-path', '-p',
                default="planner_items.csv",
                help='Path of the parsed home planner output.')
@click.option('--output-type', '-t',
                default="csv",
                help='Content type of the parsed home planner output.')
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
def parse_home_planner(verbose, home_planner_file, output_path, output_type):
    """
    Returns a Ikea Stock Checker list of items provided a home planner html document.
    At the time of writing this document is located in: 'IKEA Home Planner_files/VPUISummary.html'
    """
    items = home_planner.parse(home_planner_file)
    if output_type == "json":
        home_planner.write_json(items, output_path)
    else:
        home_planner.write_csv(items, output_path)
    if verbose: 
        click.echo("\nCreated list of ikea items\n\nInput: {} \nOutput: {} \nContentType: {}\n".format(
            home_planner_file, output_path, output_type))


@main.command()
@click.argument('stock_list', type=click.Path(exists=True))
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
def stock_check(verbose, stock_list):
    """Checks if list of provided items are in stock"""
    items = check_stock.load_input_CSV(stock_list)
    check_stock.get(items, verbose)



@main.command()
@click.argument('stock_list', type=click.Path(exists=True))
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
def add_to_shopping_list(verbose, stock_list):
    if verbose:
        click.echo(stock_list)


#         home_planner.write_csv(contents, output)
#     if stock_list and ikea_list_id:
#         if not os.environ.get('IKEA_SESSION_COOKIE'):
#             print('Session Cookie env var not set!')
#         else:
#             os.environ['IKEA_LIST_ID'] = ikea_list_id
#             items = check_stock.load_input_CSV(stock_list)
#             add_to_list.add_all(items)

if __name__ == '__main__':
    main()
