import csv
import json

from pathlib import Path

from bs4 import BeautifulSoup


def jpp(json_obj):
    """Json pretty print"""
    return json.dumps(json_obj, indent=4, sort_keys=True)


def get_items(soup):
    results = []
    try:
        item_tables = soup.find(id="summary_parent").find_all('table')
        for table in item_tables:
            rows = table.find_all('tr')
            for row in rows:
                tds = row.find_all('td')
                item = {}
                for td in tds:
                    try:
                        if td['class'][0] == 'table_item_sku':
                            item['ID'] = td.string
                        if td['class'][0] == 'table_item_quantity':
                            item['Quantity'] = td.string
                        if td['class'][0] == 'table_item_longname':
                            item['Notes'] = td.div.contents[0].string
                    except KeyError:
                        continue
                if item: 
                    results.append(item)
        return results
    except AttributeError:
        print("ERROR - Expected contents not found in the provided file.")



def write_file(file_name, contents):
    """Writes a file."""
    f = open(file_name, "w")
    f.write(contents)


def parse(input):
    """Gets inventory items from home planner html doc."""
    input = Path(input)
    if input.is_file():
        html_doc = open(input, "r")
        soup = BeautifulSoup(html_doc, 'html.parser')
        return get_items(soup)


def get_json(contens):
    """Returns pretty printed JSON."""
    return jpp(contents)


def write_json(contents, output):
    """wries pretty printed JSON."""
    write_file(output, jpp(contents))


def write_csv(contents, output):
    """"Creates ikea_check_stock formatted csv."""
    with open(output, 'w', newline='') as csvfile:
        fieldnames = ['ID', 'Quantity', 'Notes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in contents:
            writer.writerow(item)


if __name__ == '__main__':
    input = "IKEA Home Planner_files/VPUISummary.html"
    output = "order.json"
    contents = parse(input)
    write_json(contents, output)
