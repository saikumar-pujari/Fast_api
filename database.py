#this is only to connect to the database, not to create tables, that is done in models.py
#the only main part is to connect it with correct url

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = 'sqlite:///./test.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

#autocommit=False means that the session will not automatically commit changes to the database, allowing you to control when changes are saved.
#autoflush=False means that the session will not automatically flush changes to the database, allowing
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
