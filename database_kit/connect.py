from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import POSTGRES_URL

engine = create_engine(POSTGRES_URL)
Session = sessionmaker(engine)
