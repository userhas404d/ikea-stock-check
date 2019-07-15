import sys
import json


def get_json_obj(file):
    """Returns a json obj provided a file."""
    with open(file, encoding="utf8") as f:
        data = json.load(f)
    return data


def list_country_codes(store_map):
    """Returns the list of countries in the target store map."""
    store_list = []
    for store in get_json_obj(store_map):
        if store['countryCode'] not in store_list:
            store_list.append(store['countryCode'])
    return store_list


def get_ids(loc, store_map="stores.json"):
    """Returns JSON object of store IDs provided a country code."""

    # Get the command line argument. Default to 'us' if no parameter specified
    if not loc:
        loc = 'us'

    # Return all stores that match the country code
    store_ids = []
    for store in get_json_obj(store_map):
        if store['countryCode'] == loc:
            store_ids.append(store['buCode'])
    return store_ids


def get(loc, store_map="stores.json"):
    """Returns JSON object of stores provided a country code."""

    # Get the command line argument. Default to 'us' if no parameter specified
    if not loc:
        loc = 'us'

    # Return all stores that match the country code
    store_list = []
    for store in get_json_obj(store_map):
        if store['countryCode'] == loc:
            store_list.append(store)
    return store_list


if __name__ == "__main__":
    print(get(loc='us', store_map="../stores.json"))
