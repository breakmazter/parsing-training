import dramatiq
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dramatiq.middleware import TimeLimitExceeded
from dramatiq.results.errors import ResultTimeout

from sqlalchemy import create_engine, insert

import logging

from settings import *
from database_interface import devby_website_

result_backend = RedisBackend(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
broker = RabbitmqBroker(url=RABBITMQ_URL)
broker.add_middleware(Results(backend=result_backend))
dramatiq.set_broker(broker)

engine = create_engine(POSTGRES_URL, echo=True, future=True)


def should_retry(retries_so_far, exception):
    return retries_so_far < 3 and not (isinstance(exception, TimeLimitExceeded) or isinstance(exception, ResultTimeout))


@dramatiq.actor(queue_name='add_company_second_implement',
                store_results=True, max_retries=3, time_limit=180000, retry_when=should_retry)
def add_company(company_all_info):
    """
    This actor will listen to the queue, and send them to the database info about company
    """
    with engine.connect() as conn:
        conn.execute(
            insert(devby_website_),
            [company_all_info]
        )
        conn.commit()

    logging.info(f"entry for company '{company_all_info['name']}' was created.")
