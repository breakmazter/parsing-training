import dramatiq
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend
from dramatiq.brokers.rabbitmq import RabbitmqBroker

from settings import *
from actors_interface import should_retry
from actors_interface import add_company

import requests
from bs4 import BeautifulSoup


result_backend = RedisBackend(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
broker = RabbitmqBroker(url=RABBITMQ_URL)
broker.add_middleware(Results(backend=result_backend))

dramatiq.set_broker(broker)


@dramatiq.actor(queue_name='company_page_second_implement',
                store_results=True, max_retries=3, time_limit=180000, retry_when=should_retry)
def company_page(dic):
    url = dic['devby_link']

    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    company_header = soup.find("div", class_="widget-companies-header").find("div", class_="clearfix")
    contacts_div = soup.find("div", class_="sidebar-views-contacts h-card vcard")

    try:
        foundation_year = company_header.find_all("div", class_="data-info")[1].find("span").string.split()[0]
    except AttributeError:
        foundation_year = None
    try:
        industry = company_header.find("span", class_="gray").string.strip()
    except AttributeError:
        industry = None
    try:
        description = soup.find("div", class_="text").getText()
    except AttributeError:
        description = None
    try:
        label = company_header.find("img").get("src")
    except AttributeError:
        label = None
    try:
        site = contacts_div.find("a")["href"]
    except AttributeError:
        site = None
    try:
        addresses = soup.find_all("div", "info-ofice")
        location = [address.find("span").getText().strip() for address in addresses]
    except AttributeError:
        location = None
    try:
        page_views = int(contacts_div.find_all("span")[-1].getText().strip().split()[-1])
    except AttributeError:
        page_views = None

    company_info = {
        "foundation_year": foundation_year,
        "industry": industry,
        "description": description,
        "label": label,
        "site": site,
        "location": location,
        "page_views": page_views,
    }

    company_info = dic | company_info
    add_company.send(company_info)
