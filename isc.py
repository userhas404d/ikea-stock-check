import configparser
import json

import click

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
              help='Target country',
              show_default=True)
@click.option('--language',
              default='en',
              help='Language',
              show_default=True)
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
def config(verbose, store_list, country, language):
    """
    Sets the target store(s) to search.

    Accepts a comma separate list of stores.

    Example: isc.py config 119,117
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
            click.echo('\nERROR stores not found in'
                       + 'the provided country: {}.'.format(country))
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
              help=('Required to validate your store code'
                    + ' if the store is located outside the US'),
              show_default=True)
def get_stores(country):
    """
    Prints a list of stores for the target country.
    """

    store_map = "stores.json"
    country_codes = stores.list_country_codes(store_map)

    if country not in country_codes:
        click.echo('\nERROR - country code:'
                   + '{} is not a valid country code.\n'.format(country))
        click.echo('Check your country code by'
                   + ' looking at the Ikea URL of your target country')
        click.echo("For example, in the U.S. the URL is"
                   + "https://www.ikea.com/us/en/"
                   + "and the country code is \'us\'\n")
    else:
        click.echo(
            json.dumps(stores.get(loc=country, store_map=store_map),
                       indent=4, sort_keys=True))


@main.command()
@click.argument('home_planner_file', type=click.Path(exists=True))
@click.option('--output-path', '-p',
              default="planner_items.csv",
              help='Path of the parsed home planner output.',
              show_default=True)
@click.option('--output-type', '-t',
              default="csv",
              help='Content type of the parsed home planner output.',
              show_default=True)
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
def parse_home_planner(verbose, home_planner_file, output_path, output_type):
    """
    Returns a Ikea Stock Checker list of items
    provide a home planner html document.

    At the time of writing this document is located in:
    'IKEA Home Planner_files/VPUISummary.html'
    """
    items = home_planner.parse(home_planner_file)
    if output_type == "json":
        home_planner.write_json(items, output_path)
    else:
        home_planner.write_csv(items, output_path)
    if verbose:
        click.echo('\nCreated list of ikea items\n'
                   + '\nInput: {}'.format(home_planner_file)
                   + ' \nOutput: {}'.format(output_path)
                   + ' \nContentType: {}\n'.format(output_type))


@main.command()
@click.argument('stock_list', type=click.Path(exists=True))
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
def stock_check(verbose, stock_list):
    """
    Checks if list of provided items are in stock
    """
    items = check_stock.load_input_CSV(stock_list)
    check_stock.get(items, verbose)


@main.command()
@click.argument('stock_list', type=click.Path(exists=True))
@click.option('--config-path',
              default='config.ini',
              help='Path to the configuration file',
              show_default=True)
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
def add_to_shopping_list(verbose, config_path, stock_list):
    """
    Adds the provided item list to a target shopping list.
    Requires config.ini to be configured properly.

    See the README for more details.
    """

    config = configparser. RawConfigParser()
    config.read(config_path)
    # check if target config file has been populated
    for secret in config['SECRET']:
        if not config['SECRET'][secret]:
            click.echo('\nERROR: {} not set in config.ini\n'.format(secret))

    item_list = check_stock.load_input_CSV(stock_list)
    try:
        if not add_to_list.add_all(item_list, config, verbose):
            click.echo('\nERROR: Error ocurred server side'
                       + 'when adding item to list. \nPlease confirm'
                       + ' the values in config.ini are correct\n')
    except KeyError:
        click.echo('\nERROR: config.ini has not been populated properly.'
                   + '\n\nPlease re-run \'ics.py config\' and try again.\n')


if __name__ == '__main__':
    main()
