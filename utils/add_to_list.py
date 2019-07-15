import configparser
import os

import requests


# load configuration
config = configparser.ConfigParser()
try:
    IKEA_SESSION_COOKIE = config['SECRET']['IKEA_SESSION_COOKIE']
except KeyError:
    IKEA_SESSION_COOKIE = ""
try:
    IKEA_LIST_ID = config['SECRET']['IKEA_LIST_ID']
except KeyError:
    IKEA_LIST_ID = ""
try:
    IKEA_STORE_ID = config['SECRET']['IKEA_STORE_ID']
except KeyError:
    IKEA_STORE_ID = ""


def add_item(part_number, quantity):
    """Add an inventory item to a specified ikea shopping list"""
    headers = {
        "cookie": IKEA_SESSION_COOKIE,
    }

    query = {
        "partNumber": part_number,
        "langId": "-1",
        "storeId": IKEA_STORE_ID,
        "listId": IKEA_LIST_ID,
        "quantity": quantity
    }

    r = requests.get("https://www.ikea.com/webapp/wcs/stores/servlet/IrwWSInterestItemAdd", params=query, headers=headers)

    if "<msg>OK</msg>" in r.text:
        # print("Successfully added item: {0} quantity: {1} to store: {2} list: {3}".format(
        #     part_number, quantity, store_id, list_id, ))
        return True


def add_all(item_list):
    """Adds all items in a check_stock formatted csv file to an ikea shopping list."""
    for item in item_list:
        add_item(item['id'], item['qty'])
