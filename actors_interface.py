import dramatiq
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dramatiq.middleware import TimeLimitExceeded
from dramatiq.results.errors import ResultTimeout

from settings import *

result_backend = RedisBackend(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
broker = RabbitmqBroker(url=RABBITMQ_URL)
broker.add_middleware(Results(backend=result_backend))
dramatiq.set_broker(broker)


def should_retry(retries_so_far, exception):
    return retries_so_far < 3 and not (isinstance(exception, TimeLimitExceeded) or isinstance(exception, ResultTimeout))


@dramatiq.actor(queue_name='company_info_queue',
                store_results=False, max_retries=3, time_limit=180000, retry_when=should_retry)
def company_info(company_id: int, devby_link: str):
    pass


@dramatiq.actor(queue_name='update_description',
                store_results=False, max_retries=3, time_limit=180000, retry_when=should_retry)
def update_description(company_id: int, description: str):
    pass
