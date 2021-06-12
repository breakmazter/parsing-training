"""
This worker transform(cleaning from garbage and etc) text and translate to english text
"""
import logging

import dramatiq

from actors_interface import should_retry
from database_kit.connect import Session
from database_kit.crud import update_company
from googleparser import Translator
from utils.clear_text import clear_all

translator = Translator()


def translate_text(text: str) -> str:
    return translator.translate_secure(clear_all(text))['text']


@dramatiq.actor(queue_name='update_description',
                store_results=False, max_retries=3, time_limit=180000, retry_when=should_retry)
def update_description(company_id: int, description: str):

    if description:
        company_data = {
            'description': translate_text(description),
        }

        with Session() as session:
            update_company(company_id, company_data, db_session=session)
            logging.info(f"Update description for {company_id}")
            session.commit()
    else:
        logging.info(f"Not found description for {company_id}")
