from tables_model import DevbyWebsite, TfCountInfo, WebsiteInfoTransform

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from text_processing.settings import POSTGRES_URL

engine = create_engine(POSTGRES_URL)
Session = sessionmaker(bind=engine)

"""
Update information
"""


def update_company_info(company_id, company_info: dict):
    db_session = Session()
    try:
        db_session.query(DevbyWebsite).filter(DevbyWebsite.id == company_id).update(company_info)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()


def update_transform_info(com_id, trans_data: dict):
    db_session = Session()
    try:
        db_session.query(WebsiteInfoTransform).filter(WebsiteInfoTransform.company_id == com_id).update(trans_data)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()


def update_count_info(word_id, count_data: dict):
    db_session = Session()
    try:
        db_session.query(TfCountInfo).filter(TfCountInfo.id == word_id).update(count_data)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()


"""
Create information
"""


def create_company_info(company_info: dict):
    db_session = Session()
    obj = DevbyWebsite(
                               name=company_info['name'],
                               devby_link=company_info['devby_link'],
                               employees_amount=company_info['employees_amount'],
                               careers_link=company_info['careers_link'],
                               mark=company_info['mark'],
                               reviews_amount=company_info['reviews_amount'],
                               reviews_link=company_info['reviews_link'],
                               discussions_amount=company_info['discussions_amount'],
                               discussions_link=company_info['discussions_link'],
                               foundation_year=company_info['foundation_year'],
                               industry=company_info['industry'],
                               description=company_info['description'],
                               label=company_info['label'],
                               site=company_info['site'],
                               location=company_info['location'],
                               page_views=company_info['page_views']
    )
    try:
        db_session.add(obj)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()


def create_transform_info(trans_data: dict):
    db_session = Session()
    obj = WebsiteInfoTransform(
        company_id=trans_data['company_id'],
        description_2trans=trans_data['description_2trans'])
    try:
        db_session.add(obj)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()


def create_count_info(count_data: dict):
    db_session = Session()
    obj = TfCountInfo(count_word_in_all_space=count_data['count_word_in_all_space'])
    try:
        db_session.add(obj)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()
