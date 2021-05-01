from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, REAL
from sqlalchemy.orm import relationship


Base = declarative_base()


class DevbyWebsite(Base):
    __tablename__ = "devby_website"
    id = Column(Integer, primary_key=True)
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
    industry = Column(String)
    description = Column(String)
    label = Column(String)
    site = Column(String)
    location = Column(String)
    page_views = Column(String)

    info_transform = relationship("WebsiteInfoTransform", back_populates="devby_web")

    def __repr__(self):
        return f"<Devby_Website({self.id, self.name, self.site})>"


class WebsiteInfoTransform(Base):
    __tablename__ = "website_info_transform"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('devby_website.id'), index=True)
    description_2trans = Column(String)

    devby_web = relationship("DevbyWebsite", back_populates="info_transform")

    def __repr__(self):
        return f"<WebsiteInfoTransform({self.id, self.description_trans})>"


class TfCountInfo(Base):
    __tablename__ = "tf_count_info"

    id = Column(Integer, primary_key=True)
    word = Column(String)
    count_word_in_all_space = Column(Integer)
    tf_word_in_all_space = Column(REAL)

    def __repr__(self):
        return f"<TfCountInfo({self.external_id, self.created_at})>"
