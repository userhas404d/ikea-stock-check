import configparser
import json

from utils import stores


config = configparser.ConfigParser()
ikea_stores = stores.IkeaStores()


class isc_config():
    def __init__(self, config_path=""):
        if config_path:
            config.read(config_path)
        else:
            config.read('config.ini')

    def get(self):
        loaded_config = {}

        try:
            loaded_config['store_ids'] = json.loads(
                config['CONFIG']['IKEA_STORES'])
        except KeyError:
            print('Using default stores: [215, 211]')
            loaded_config['store_ids'] = [215, 211]

        try:
            loaded_config['country_code'] = (
                config['CONFIG']['IKEA_COUNTRY_CODE'])
        except KeyError:
            print('Using default country code: us')
            loaded_config['country_code'] = 'us'

        try:
            loaded_config['language_code'] = (
                config['CONFIG']['IKEA_LANG_CODE'])
        except KeyError:
            print('Using default language code: en')
            loaded_config['language_code'] = 'en'

        loaded_config['store_names'] = (
            ikea_stores.get_store_names(loaded_config['store_ids'])
            )

        try:
            loaded_config['SECRET']['IKEA_SESSION_COOKIE'] = (
                config['SECRET']['IKEA_SESSION_COOKIE'])
            loaded_config['SECRET']['IKEA_STORE_ID'] = (
                config['SECRET']['IKEA_STORE_ID'])
            loaded_config['SECRET']['IKEA_LIST_ID'] = (
                config['SECRET']['IKEA_LIST_ID'])
        except KeyError:
            loaded_config['SECRET'] = None

        return loaded_config
