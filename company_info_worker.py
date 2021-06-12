"""
This worker transform(cleaning from garbage and etc) text and translate to english text
"""

import logging

import dramatiq
import requests
from bs4 import BeautifulSoup

from actors_interface import should_retry, update_description
from database_kit.connect import Session
from database_kit.crud import is_industry, update_company, add_industry, add_company_industry
from settings import HEADERS


def clean_industry(mass):
    return [word.strip().lower() for word in mass if word.strip().lower()]


@dramatiq.actor(queue_name='company_info_queue',
                store_results=False, max_retries=3, time_limit=180000, retry_when=should_retry)
def company_info(company_id: int, devby_link: str):
    html_soup_data = BeautifulSoup(requests.get(devby_link, headers=HEADERS).text, "html.parser")

    company_header = html_soup_data.find("div", class_="widget-companies-header").find("div", class_="clearfix")
    contacts_div = html_soup_data.find("div", class_="sidebar-views-contacts h-card vcard")

    try:
        foundation_year = company_header.find_all("div", class_="data-info")[1].find("span").string.split()[0]
    except AttributeError:
        foundation_year = None
    try:
        industry = company_header.find("span", class_="gray").string.strip()
    except AttributeError:
        industry = None
    try:
        description = html_soup_data.find("div", class_="text").getText()
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
        addresses = html_soup_data.find_all("div", "info-ofice")
        location = [address.find("span").getText().strip() for address in addresses]
    except AttributeError:
        location = None
    try:
        page_views = int(contacts_div.find_all("span")[-1].getText().strip().split()[-1])
    except AttributeError:
        page_views = None

    industries = clean_industry(industry.split(', '))

    company_data = dict(
        foundation_year=foundation_year, site=site,
        description=description, label=label,
        location=location, page_views=page_views
    )

    with Session() as session:
        for industry in industries:
            try:
                if not is_industry(industry, db_session=session):
                    add_industry({'industry_id': industry}, db_session=session)

                add_company_industry(company_id, industry, db_session=session)

                session.flush()
            except Exception as e:
                session.rollback()
                raise e

        update_company(company_id, company_data, db_session=session)

        update_description.send(company_id, description)

        logging.info(f"{company_id} ---> update data!!!")
        session.commit()
