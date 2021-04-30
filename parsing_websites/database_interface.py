from sqlalchemy import create_engine, Column, Integer, String, Table, MetaData, ForeignKey, REAL
from settings import *

engine = create_engine(POSTGRES_URL, echo=True, future=True)
metadata = MetaData()

devby_website_ = Table(
    "devby_website",
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('devby_link', String),
    Column('employees_amount', String),
    Column('careers_link', String),
    Column('mark', String),
    Column('reviews_amount', String),
    Column('reviews_link', String),
    Column('discussions_amount', String),
    Column('discussions_link', String),
    Column('foundation_year', String),
    Column('industry', String),
    Column('description', String),
    Column('label', String),
    Column('site', String),
    Column('location', String),
    Column('page_views', String),
)


website_info_transf_ = Table(
    "website_info_transform",
    metadata,
    Column('id', Integer, primary_key=True),
    Column('company_id', ForeignKey('devby_website.id')),
    Column('description_trans', String),
)


tf_count_info_ = Table(
    "tf_count_info",
    metadata,
    Column('id', Integer, primary_key=True),
    Column('word', String),
    Column('count_word_in_all_space', Integer),
    Column('tf_word_in_all_space', REAL),
)




