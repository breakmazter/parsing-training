"""
This worker transform(cleaning from garbage and etc) text and translate to english text
"""
import dramatiq

from actors_interface import should_retry
from googleparser import Translator
from utils.clear_text import clear_all

from database_kit.crud import update_company
from database_kit.connect import Session

translator = Translator()


def translate_text(text: str) -> str:
    return translator.translate_secure(clear_all(text))['text']


@dramatiq.actor(queue_name='clear_translate_second_implement',
                store_results=True, max_retries=3, time_limit=180000, retry_when=should_retry)
def update_description(company_id, description: str):
    company_data = {
        'description_2trans': translate_text(description),
    }

    with Session() as session:
        update_company(company_id, company_data, db_session=session)
