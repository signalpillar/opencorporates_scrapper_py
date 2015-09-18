# -*- coding: utf-8 -*-
"""
Target URL: http://www.nbrb.by/engl/system/register.asp?bank=133
Every bank has a:
 - name: str
 - Open Joint–Stock Company: str
 - Banking license number: str
 - issue date: date
 - operations: list[str] ?
"""

# std
from __future__ import print_function
import collections
import datetime
import itertools as it
import json
import re

# 3rd-party
import requests
from bs4 import BeautifulSoup as bs


BankDetails = collections.namedtuple('BankDetails', 'name full_name license_number issue_date')
BankId = collections.namedtuple("BankId", "id name")


BANK_DETAILS_URL_TEMPLATE = "http://www.nbrb.by/engl/system/register.asp?bank={}"


def strip_enclosing(value, start_symb, end_symb=None):
    end_symb = end_symb or start_symb
    if value.startswith(start_symb) and value.endswith(end_symb):
        value = value[1:-1]
    return value


def remove_tags(value, tag_name):
    return value.replace(
        '<{}>'.format(tag_name), ''
    ).replace(
        '</{}>'.format(tag_name), ''
    )


is_even = lambda x: x % 2 == 0


def strip_spare(value):
    if value:
        value = strip_enclosing(value.strip(), '(', ')')
        quotes_num = value.count('"')
        if quotes_num and is_even(quotes_num):
            value = strip_enclosing(value, '"')
        value = remove_tags(value, 'b')
    return value


def parse_select_options(select_el):
    return [
        (option_el.attrs.get('value'), option_el.text)
        for option_el in select_el.find_all('option')
    ]


def parse_ul_list_items(ul_el):
    return [
        strip_spare(li_el.text)
        for li_el in ul_el.find_all('li')
    ]


def parse_list_of_banks(content):
    return next((
        parse_select_options(el)
        for el in bs(content).find_all('select')
        if el.attrs.get('name') == "bank"
    ), ())


def parse_bank_name(content):
    '''str -> str -> tuple[str?, str?]

    Example of the HTML to find::

        </form>
        Open Joint–Stock Company <b>"Paritetbank"</b>(OJSC "Paritetbank")

    In parentheses we have a full name, but it is an optional value.

    Result of sample parsing::

        ("Open Joint–Stock Company \"Paritetbank\"", "OJSC \"Paritetbank\"")
    '''
    matched = re.search('</form>(.+?)(\(.*?)?<br>', content, re.DOTALL)
    if matched:
        return map(strip_spare, matched.groups())
    return None, None


def parse_license(content):
    'str -> tuple[str, str]'
    matched = re.search('\s+Banking License\s*'
                        '<b>\s*No.\s+(\w*?)</b>\s*,'
                        '\s*was\s+issued\s+on\s*<b>(.*?)</b>', content)
    if matched:
        return map(strip_spare, matched.groups())


def parse_operations(el):
    operations_list_classes = ["withtit"]
    return next((
        parse_ul_list_items(list_el)
        for list_el in el.find_all('ul')
        if list_el.attrs.get('class') == operations_list_classes
    ), ())


def parse_bank_details(content):

    full_name, name = parse_bank_name(content)
    license_number, licese_issue_date = parse_license(content)

    return BankDetails(
        name=name,
        full_name=full_name,
        license_number=license_number,
        issue_date=licese_issue_date,
    )


def get_banks(url):
    response = requests.get(url)
    if response.status_code == 200:
        return (
            BankId(id_, name)
            for (id_, name) in parse_list_of_banks(response.content)
        )
    raise RuntimeError("Failed to get list of banks: {}".format(response.content))


def get_bank_detials(base_url, id_):
    response = requests.get(BANK_DETAILS_URL_TEMPLATE.format(id_))
    if response.status_code == 200:
        return parse_bank_details(response.content)
    raise RuntimeError("Failed to get bank {!r} details: {!r}".format(id_, response.content))


FINANCIAL_CATEGORY = "Financial"


def main(base_url, start_url):
    bank_ids, ids_for_output = it.tee(get_banks(start_url))

    details = it.imap(lambda bank_id: get_bank_detials(base_url, bank_id.id), bank_ids)

    for bank_id, details in it.izip(ids_for_output, details):
        if not details.name:
            details = details._replace(name=bank_id.name)
        bank_details_dict = details._asdict()
        bank_details_dict.update(dict(
            company_name=details.name,
            category=FINANCIAL_CATEGORY,
            source_url=BANK_DETAILS_URL_TEMPLATE.format(bank_id.id),
            sample_date=datetime.datetime.now().isoformat()))

        print(json.dumps(bank_details_dict))


if __name__ == "__main__":
    main(base_url="http://www.nbrb.by/", start_url=BANK_DETAILS_URL_TEMPLATE.format(108))
