"""
This worker transform(cleaning from garbage and etc) text and translate to english text
"""
import dramatiq
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dramatiq.middleware import TimeLimitExceeded
from dramatiq.results.errors import ResultTimeout

from database_pr.tables_crud import create_transform_info
from clear_text import clear_all

from settings import *

from word2word import Word2word


translate = Word2word("ru", "en")

result_backend = RedisBackend(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
broker = RabbitmqBroker(url=RABBITMQ_URL)
broker.add_middleware(Results(backend=result_backend))
dramatiq.set_broker(broker)


def should_retry(retries_so_far, exception):
    return retries_so_far < 3 and not (isinstance(exception, TimeLimitExceeded) or isinstance(exception, ResultTimeout))


# TODO bad work translate
def translate_text(text: str) -> str:
    mass_str = text.split()
    mass_trans = []

    for s in mass_str:
        tr_word = s
        try:
            tr_word = translate(s, n_best=2)[1]
        except KeyError:
            pass

        mass_trans.append(tr_word)

    return ' '.join(mass_trans)


@dramatiq.actor(queue_name='clear_translate_second_implement',
                store_results=True, max_retries=3, time_limit=180000, retry_when=should_retry)
def clear_translate_description(company_id, description: str):
    dic = {'company_id': company_id, 'description_2trans': clear_all(translate_text(description))}
    create_transform_info(dic)

