from sqlalchemy import (
    # BigInteger,
    Column,
    ForeignKey,
    Integer,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    # relationship,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension(keep_session=True)))
Base = declarative_base()

class Feed(Base):
    __tablename__ = 'feeds'
    id = Column(Text, primary_key=True)
    name = Column(Text)
    archive_url = Column(Text, nullable=False)
    time_between_posts = Column(Integer, nullable=False)
    time_created = Column(Integer, nullable=False)
    user = Column(ForeignKey('users.id'))
    most_recent_page = Column(ForeignKey('pages.id'))


""" A Page represents one post on the website. There will be many of these
for each feed"""
class Page(Base):
    __tablename__ = 'pages'
    archive_url = Column(Text)
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    page_url = Column(Text)
    description = Column(Text)
    time_created = Column(Text, nullable=False)
    

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    google_id = Column(Text, unique=True)
    email = Column(Text)

    ##############
    # feed = Feed(name=title, data="TESTY1")
    # DBSession.add(feed)
