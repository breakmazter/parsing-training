import logging

from sqlalchemy import exc, insert

from database_kit.models import Company, Industry, CompanyIndustry


def add_company(company_info: dict, db_session):
    obj = Company(**company_info)
    try:
        db_session.add(obj)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()


def add_industry(industry_info: dict, db_session):
    obj = Industry(**industry_info)
    try:
        db_session.add(obj)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()


def is_industry(industry, db_session):
    try:
        return db_session.query(
            db_session.query(Industry.industry_id).filter_by(industry_id=industry).exists()
        ).scalar()
    except Exception as e:
        db_session.rollback()
        raise e


def update_company(company_id, company_data, db_session):
    try:
        db_session.query(Company).filter_by(company_id=company_id).update(company_data)
        db_session.flush()
    except Exception as e:
        if isinstance(e, exc.IntegrityError):
            logging.info("Integrity Error")
        elif isinstance(e, exc.PendingRollbackError):
            logging.info("Pending Rollback Error")
        else:
            logging.info("Unknown Error")

        logging.info("Pending Rollback Error")
        
        
def add_company_industry(company_id, industry_id, db_session):
    try:
        data = insert(CompanyIndustry).values(company_id=company_id, industry_id=industry_id)
        db_session.execute(data)
        db_session.flush()
    except Exception as e:
        if isinstance(e, exc.IntegrityError):
            logging.info("Integrity Error")
        elif isinstance(e, exc.PendingRollbackError):
            logging.info("Pending Rollback Error")
        else:
            logging.info("Unknown Error")

        logging.info("Pending Rollback Error")
