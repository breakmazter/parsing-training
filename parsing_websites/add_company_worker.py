import dramatiq
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dramatiq.middleware import TimeLimitExceeded
from dramatiq.results.errors import ResultTimeout

from actors_interface import clear_translate_description

import logging

from database_pr.tables_crud import create_company_info
from settings import *

result_backend = RedisBackend(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
broker = RabbitmqBroker(url=RABBITMQ_URL)
broker.add_middleware(Results(backend=result_backend))
dramatiq.set_broker(broker)


def should_retry(retries_so_far, exception):
    return retries_so_far < 3 and not (isinstance(exception, TimeLimitExceeded) or isinstance(exception, ResultTimeout))


@dramatiq.actor(queue_name='add_company_second_implement',
                store_results=True, max_retries=3, time_limit=180000, retry_when=should_retry)
def add_company(company_all_info: dict):
    """
    This actor will listen to the queue, and send them to the database_pr info about company
    """
    clear_translate_description.send(company_all_info['id'], company_all_info['description'])

    del company_all_info['id']
    create_company_info(company_all_info)

    logging.info(f"entry for company '{company_all_info['name']}' was created.")
