from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, func, create_engine
from sqlalchemy.orm import relationship, backref

from settings import POSTGRES_URL

Base = declarative_base()
engine = create_engine(POSTGRES_URL)

CompanyIndustry = Table('company_industry', Base.metadata,
                        Column('company_id', Integer, ForeignKey('company.company_id'), primary_key=True),
                        Column('industry_id', String, ForeignKey('industry.industry_id'), primary_key=True))


class Company(Base):
    __tablename__ = "company"

    company_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    devby_link = Column(String)
    employees_amount = Column(String)
    careers_link = Column(String)
    mark = Column(String)
    reviews_amount = Column(String)
    reviews_link = Column(String)
    discussions_amount = Column(String)
    discussions_link = Column(String)
    foundation_year = Column(String)
    description = Column(String)
    label = Column(String)
    site = Column(String)
    location = Column(String)
    page_views = Column(String)

    created_at = Column(DateTime, server_default=func.now())
    modified_at = Column(DateTime, onupdate=func.now())

    industries = relationship(
        'Industry', secondary=CompanyIndustry, backref=backref('companies', lazy='dynamic'), lazy='dynamic'
    )

    def __repr__(self):
        return f"<Company({self.company_id, self.name})>"


class Industry(Base):
    __tablename__ = "industry"

    industry_id = Column(String, primary_key=True, index=True)

    created_at = Column(DateTime, server_default=func.now())
    modified_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<Industry({self.industry_id, self.description_trans})>"


def create_all_tables(engine):
    try:
        Base.metadata.create_all(engine)
        print('tables was created.')
    except Exception as e:
        print(e)
