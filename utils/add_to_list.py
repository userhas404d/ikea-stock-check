import requests

from utils import load_config


# load the config
ISC_CONFIG = load_config.isc_config().get()


def add_item(part_number, quantity, verbose=False):
    """Add an inventory item to a specified ikea shopping list"""

    if ISC_CONFIG['SECRET']:
        SESSION_COOKIE = ISC_CONFIG['SECRET']['IKEA_SESSION_COOKIE']
        STORE_ID = ISC_CONFIG['SECRET']['IKEA_STORE_ID']
        LIST_ID = ISC_CONFIG['SECRET']['IKEA_LIST_ID']
    else:
        print(
            '\nERROR: SECRETS have not been configured'
            ' in the provided config.ini\n')
        quit()

    headers = {
        "cookie": SESSION_COOKIE,
    }

    query = {
        "partNumber": part_number,
        "langId": "-1",
        "storeId": STORE_ID,
        "listId": LIST_ID,
        "quantity": quantity
    }

    add_item_url = ("https://www.ikea.com"
                    + "/webapp/wcs/stores/servlet/IrwWSInterestItemAdd"
                    )
    r = requests.get(add_item_url, params=query, headers=headers)

    if r.status_code != "404":
        if verbose:
            print("\nAdded"
                  + "\nitem: {0}".format(part_number)
                  + " \nquantity: {1}".format(quantity)
                  + " \nstore: {2}".format(STORE_ID)
                  + " \nlist: {3}\n".format(LIST_ID)
                  )
        return True


def add_all(item_list, verbose=False):
    """
    Adds all items in a check_stock formatted csv file
    to an ikea shopping list.
    """
    for item in item_list:
        if not add_item(item['id'], item['qty'], verbose):
            return False
    return True
