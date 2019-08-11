# IKEA Stock Check

A super convenient way to make a shopping list for IKEA.

## Features

For specified IKEA article numbers, this tool checks the stock and provides the aisle and bin locations for stores nearby.

*NEW* Enables the creation of a shopping list provided an [ikea kitchen planner](https://kitchenplanner.ikea.com/us/UI/Pages/VPUI.htm) item list

*NEW* Add your local shopping list to an online shopping list via your ikea account

## Installation

* Install [Python 3](https://www.python.org/) on your system (or check that it is installed and enabled in your environment)
* Clone this repository and navigate to the downloaded directory
* In your terminal: `pip install -r requirements.txt`

## Set Preferred Stores

* If you are in the U.S., run `python isc.py get-stores` (or `python3 isc.py get-stores`)

   ![U.S. Store Codes](images/us_store_codes.png)

* Otherwise, figure out your 2-digit country code and language code. You can find this by going to your country's IKEA website. In the URL [https://www.ikea.com/jp/ja/](https://www.ikea.com/jp/ja/), 'jp' is the country code and 'ja' is the language code. Then run the same program with your country code, e.g. `python isc.py get-stores --country jp`.

   ![Country and Language Codes](images/country_language_codes.png)

   ![Japan Store Codes](images/japan_store_codes.png)

* Find your preferred store(s) and note their 3-digit codes. For example, the store in PA, South Philadelphia has the code 215.
* Run `python isc.py config` targeting your preferred stores, language code, and country code, e.g. `python isc.py config 215,168` if you are targeting a different country and/or language add the `--country` and `--language` flags respectively. Alternatively, you can edit `config.ini` directly

   ![config.ini](images/config_stores.png)

## Check Stock and Locations

* Find the article numbers of the items you would like to purchase. They can be recorded with or without the period separators (e.g. 202.813.82 and 20281382 are both valid).

   **However,** I recommend copying the item code from the product's URL, as it sometimes differs from the article number listed on the site. For example, the article number for the [STUVA wall shelf](https://www.ikea.com/us/en/catalog/products/S79276717/) is 792.767.17, but the URL specifies it as S79276717. Only the number from the URL (S79276717) works in the IKEA API.

   ![url_article_number](images/url_article_number.png)

* Edit the file `in.csv` with the item id(s). (Optionally, include the quantity you need, and any notes. If you do not include a quantity, it will be assumed as 1.)

   ![in.csv](images/in_csv.png)

   **Note:** I recommend editing the CSV file in a text editor (e.g. Notepad, TextEdit, or [Visual Studio Code](https://code.visualstudio.com/)) and not Microsoft Excel, as Excel likes to play with formatting. You must include two commas on every line.

* Run the script: `python isc.py check-stock in.csv`. You'll see the status of the script, as well as any errors if they arise. When the script is finished, you'll have a CSV file for each store, saved as out_[store name].csv. This is what it looks like:

![output](images/out.png)

A few things to note about the output file:

* 'In-Stock Confidence' is the probability at least qty 1 will still be in stock when you arrive at the store
* 'Meets Qty Reqs' will show True if the store has your desired quantity for every item on the list, False if not
* Any items that are short on quantity will show NOT ENOUGH QTY! in the notes section
* Total items is the total number of items you should have in your cart at the end of the trip
* Total Price is the total price of the cart, not including IKEA Family pricing
* For multi-piece items, each item will be broken down into a separate line item, as these are often located in different areas of the store. The quantity is updated based on how many you need

## Parse a kitchen planner list

* From the [ikea kitchen planner](https://kitchenplanner.ikea.com/us/UI/Pages/VPUI.htm) interface, select the `Item List/Total price` button.
* Right click on the resulting popup and select `Save as.. > Webpage, Complete`
* Once the list has been saved extract the item list `python isc.py parse-home-planner '..\ikea_kitchen_builder\IKEA Home Planner_files\VPUISummary.html' -v`
* View the results in the `planner_items.csv` file that was generated

## Add a local item list to a ikea shopping list

* Populate `config.ini` with the required information

1. Login to the [ikea website](https://www.ikea.com/us/en/)
2. Find a test item to add to your list. Or just use [this link](https://www.ikea.com/us/en/catalog/products/20011408/)
3. Open the developer console (F12)
4. From the developer console, select the network tab
5. Press the clear button to remove the previously recorded actions
6. Add the item to your target shopping list
7. From the developer console, find recorded `IrwWSInterestItemAdd?` action
8. Copy the recoded cookie to the assigned value of `ikea_session_cookie` in your `config.ini`
9. Do the same for the `ikea_list_id` and `ikea_store_id`. Both of these can be found in the `:path:` value of the `Request Headers` section

* Once your `config.ini` has been populated you can now use isc' `add-to-shopping-list` command as follows:

```bash
python isc.py add-to-shopping-list planner_items.csv
```

## Caveats

* There are almost definitely bugs with these scripts! I'm fixing them as I encounter them. If you notice anything, please open an issue or submit a pull request.
* Please don't run a large number of requests (100s per hour or day). The API provided by IKEA was really only meant for their own website, and they might not be happy with a large quantity of requests.
* The IKEA API could change at any time. It may also differ by country. I've only tested this in the U.S.
* I've only tested this with Python 3.7 on Mac.

## Need Help?

Please open an issue on this repository or [contact me](https://gregyeutter.com/connect).

## Was this project useful?

Consider [buying me a coffee](https://buymeacoff.ee/gregyeutter) or [donating via PayPal](https://www.paypal.me/gregyeutter/).

## License

This project is distributed under the [MIT license](/LICENSE).
