
import pandas
import re as regex

from http.client import IncompleteRead
from urllib.parse import urlencode
from copy import deepcopy
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup

def data_extractor(card):
  price_element = card.find("span", { "class": "mainValue" })
  name_element = card.find("a", { "class": "name" })
  store_count_element = card.find("a", { "class": "storeCount" })

  return {
    "price": price_element.get_text() if price_element else None,
    "name": name_element.get_text() if name_element else None,
    "store_count": store_count_element.get_text() if store_count_element else None
  }


def data_parser(smartphone):
  try:
    smartphone = deepcopy(smartphone)

    smartphone["price"] = int(regex.sub(r"[^0-9]", "", smartphone.get("price"))) * 100 if smartphone.get("price") else None
    smartphone["price_cents"] = smartphone.pop("price") # Renaming key from "price" to "price_cents"
    smartphone["store_count"] = int(regex.sub(r"[^0-9]", "", smartphone.get("store_count"))) if smartphone.get("store_count") else None

    return smartphone
  except Exception as e:
    print(f"Exception: {e}")
    print(f"smartphone: {smartphone}")

def create_data_frame(soup, device_model):
    search_result_element = soup.find("div", { "id": "pageSearchResultsBody" })
    cards = search_result_element.find_all("div", { "class": "card card--prod" })
    smartphones_raw_data = list(map(data_extractor, cards))
    for data in smartphones_raw_data:
      data["device_model_searched"] = device_model

    smartphones_formatted_data = list(map(data_parser, smartphones_raw_data))

    return pandas.DataFrame(smartphones_formatted_data)

# Treating IncompleteRead errors when requesting
# This is a zoom server problem so we need this workaround to keep using zoom
# Not necessary if using other sites.
def html_reader(response):
    try:
        html = response.read().decode("utf-8")
        print("[SUCCESS] html file could be read without problems")
        return html
    except IncompleteRead as e:
        print("[WARN] something went wrong when reading html so the file can be smaller")
        return e.partial

def request_smartphone_info(device_model):
    search_params = { "q": device_model }
    base_url = f"https://www.zoom.com.br/search?{urlencode(search_params)}"
    headers = { "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36" }

    try:
        request = Request(base_url, headers=headers)
        response = urlopen(request, timeout=30)
        html = html_reader(response)
        return BeautifulSoup(html, "html.parser")
    except HTTPError as error:
        print(f"HTTPError: {error}")
    except URLError as error:
        print(f"URLError: {error}")
    except Exception as exception:
        print(f"Exception: {exception}")
