import json


class IkeaStores():
    """Ikea store class"""
    def __init__(self,
                 store_map='stores.json',
                 country_code='us'
                 ):
        self.store_map = get_json_obj(store_map)
        self.country_code = country_code

    def list_country_codes(self):
        """
        Returns the list of countries in the target store map.
        """
        store_list = []
        for store in self.store_map:
            if store['countryCode'] not in store_list:
                store_list.append(store['countryCode'])
        return store_list

    def get(self):
        """
        Returns JSON object of stores provided a country code.
        """

        # Return all stores that match the country code
        store_list = []
        for store in self.store_map:
            if store['countryCode'] == self.country_code:
                store_list.append(store)
        return store_list

    def get_ids(self):
        """
        Returns JSON object of store IDs.
        """

        store_ids = []
        for store in self.store_map:
            if store['countryCode'] == self.country_code:
                store_ids.append(store['buCode'])
        return store_ids

    def get_store_names(self, store_ids):
        """
        Gets the store name from the store ID

        Inputs:
            store_id int: The store ID

        Returns: The store name
        """
        store_names = []
        for store_id in store_ids:
            for store in self.store_map:
                if store['buCode'] == store_id:
                    store_names.append(
                            {
                                'id': store_id,
                                'name': store['name']
                            }
                        )
        return store_names

    def is_valid_store(self, store_id_list):
        for store in store_id_list:
            if store in self.get_ids():
                return True

    def is_valid_country_code(self, code):
        country_codes = self.list_country_codes()
        if code in country_codes:
            return True


def get_json_obj(file):
    """Returns a json obj provided a file."""
    with open(file, encoding="utf8") as f:
        data = json.load(f)
    return data


if __name__ == "__main__":
    stores = IkeaStores(store_map='../stores.json')
    print(stores.get())
