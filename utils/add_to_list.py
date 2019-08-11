import requests


def add_item(part_number, quantity, config, verbose=False):
    """Add an inventory item to a specified ikea shopping list"""

    session_cookie = config['SECRET']['IKEA_SESSION_COOKIE']
    store_id = config['SECRET']['IKEA_STORE_ID']
    list_id = config['SECRET']['IKEA_LIST_ID']

    headers = {
        "cookie": session_cookie,
    }

    query = {
        "partNumber": part_number,
        "langId": "-1",
        "storeId": store_id,
        "listId": list_id,
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
                  + " \nstore: {2}".format(store_id)
                  + " \nlist: {3}\n".format(list_id)
                  )
        return True


def add_all(item_list, config, verbose=False):
    """
    Adds all items in a check_stock formatted csv file
    to an ikea shopping list.
    """
    for item in item_list:
        if not add_item(item['id'], item['qty'], config, verbose):
            return False
    return True
