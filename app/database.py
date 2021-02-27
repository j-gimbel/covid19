from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from os import environ

# SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

database_url = environ["SQLALCHEMY_DATABASE_URL"]
connect_args = {}

if "sqlite" in database_url:
    connect_args["check_same_thread"] = False

engine = create_engine(environ["SQLALCHEMY_DATABASE_URL"], connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
