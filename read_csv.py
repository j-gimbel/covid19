import sqlite3
from sqlalchemy.orm import Session
from app import models  # ,crud,  schemas
from app.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()


if __name__ == "__main__":

    f = open("e:/full-data.csv", "r")

    line = f.readline()
    headers = line.split(",")

    while True:
        line = f.readline()
        if line == "" or line == None:
            break

        d = line.split(",")

        # hier weiter
