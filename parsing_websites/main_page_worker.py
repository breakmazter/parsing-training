import dramatiq
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend
from dramatiq.brokers.rabbitmq import RabbitmqBroker

from settings import *
from actors_interface import company_page

import requests
from bs4 import BeautifulSoup


result_backend = RedisBackend(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
broker = RabbitmqBroker(url=RABBITMQ_URL)
broker.add_middleware(Results(backend=result_backend))

dramatiq.set_broker(broker)


if __name__ == "__main__":
    response_text = requests.get(MAIN_PAGE, headers=HEADERS).text
    soup = BeautifulSoup(response_text, "html.parser")

    table = soup.find('table', {"id": "tablesort"})
    table_body = table.find('tbody')

    data = table_body.find_all('tr')

    for row, i in zip(data, range(len(data))):
        cells = row.findAll("td")

        dic = {
            "id": i,
            "name": cells[0]["data"],
            "devby_link": MAIN_PAGE + cells[0].find("a")["href"],
            "employees_amount": int(cells[2].string.strip()),
            "careers_link": cells[3].find("a")["href"],
            "mark": float(cells[1]["data"])}

        if dic["mark"] == 0:
            dic["mark"] = None

        dic["reviews_amount"] = int(cells[4]["data"].strip())
        if dic["reviews_amount"] > 0:
            dic["reviews_link"] = MAIN_PAGE + cells[4].find("a")["href"]
        else:
            dic["reviews_link"] = None

        dic["discussions_amount"] = int(cells[5]["data"].strip())
        if dic["discussions_amount"] > 0:
            dic["discussions_link"] = MAIN_PAGE + cells[5].find("a")["href"]
        else:
            dic["discussions_link"] = None

        company_page.send(dic)