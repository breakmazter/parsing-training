import requests
from bs4 import BeautifulSoup

from actors_interface import company_info
from database_kit.connect import Session
from database_kit.crud import add_company
from settings import *


def main_page_worker():
    response_text = requests.get(MAIN_PAGE, headers=HEADERS).text
    soup = BeautifulSoup(response_text, "html.parser")

    main_page_data = soup.find('table', {"id": "tablesort"}).find('tbody').find_all('tr')

    for i, row in enumerate(main_page_data):
        cells = row.findAll("td")

        company_data = {
            "company_id": i,
            "name": cells[0]["data"],
            "devby_link": MAIN_PAGE + cells[0].find("a")["href"],
            "employees_amount": int(cells[2].string.strip()),
            "careers_link": cells[3].find("a")["href"],
            "mark": float(cells[1]["data"])
        }

        if company_data["mark"] == 0:
            company_data["mark"] = None

        company_data["reviews_amount"] = int(cells[4]["data"].strip())
        if company_data["reviews_amount"] > 0:
            company_data["reviews_link"] = MAIN_PAGE + cells[4].find("a")["href"]
        else:
            company_data["reviews_link"] = None

        company_data["discussions_amount"] = int(cells[5]["data"].strip())
        if company_data["discussions_amount"] > 0:
            company_data["discussions_link"] = MAIN_PAGE + cells[5].find("a")["href"]
        else:
            company_data["discussions_link"] = None

        with Session() as session:
            add_company(company_data, db_session=session)
            company_info.send(i, company_data['devby_link'])
            
            print(f"{company_data['name']} ---> data added")
            
            session.commit()


if __name__ == "__main__":
    main_page_worker()
