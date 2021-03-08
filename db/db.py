import sqlite3
import json
from sqlalchemy.orm import Session, load_only
import logging
import requests
import os
import csv
import shutil
import gzip
import glob
import re
from datetime import date, datetime, timedelta

from app import models  # ,crud,  schemas
from app.database import SessionLocal, engine


def read_data_from_csv(csv_file_path: str, expected_header_line: str):
    rows = []
    csv_reader = csv.reader(open(csv_file_path, "rt", encoding="utf-8"))
    for row in csv_reader:
        rows.append(row)
    column_names = expected_header_line.split(",")
    if rows[0] != column_names:
        raise Exception("Bad Header in " + csv_file_path)
    header = rows[0]
    indexes = {}
    for col in column_names:
        indexes[col] = header.index(col)
    rows.pop(0)
    return {"rows": rows, "indexes": indexes}


class DB:
    def __init__(self):

        models.Base.metadata.create_all(bind=engine)
        self.session = SessionLocal()

        # create logger
        self.logger = logging.getLogger("create_db")
        self.logger.setLevel(logging.DEBUG)
        # create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # add formatter to ch
        ch.setFormatter(formatter)
        # add ch to logger
        self.logger.addHandler(ch)
        # create file handler and set level to debug
        fh = logging.FileHandler("create_db.log")
        fh.setLevel(logging.DEBUG)
        # add formatter to ch
        fh.setFormatter(formatter)
        # add ch to logger
        self.logger.addHandler(fh)

    def _clear_db(self):
        print("clearing")
        self.session.close()
        print(os.path.dirname(__file__) + "/../database.db")
        os.remove(os.path.dirname(__file__) + "/../database.db")
        # print(models.Base.metadata.tables.values())
        # models.Base.metadata.drop_all(bind=engine)
        models.Base.metadata.create_all(bind=engine)
        self.session = SessionLocal()

    def _insert_bundeslaender_landkreise_altersgruppen(self, data):

        data_bundeslaender = {}

        altersgruppen = []
        for row in data["rows"]:
            ### Altersgruppen
            altersgruppe = row[data["indexes"]["Altersgruppe"]]
            if altersgruppe not in altersgruppen:
                altersgruppen.append(altersgruppe)
            Meldedatum = row[data["indexes"]["Meldedatum"]]

            ### Bundesland

            IdBundesland = row[data["indexes"]["IdBundesland"]]
            if not str(IdBundesland) in data_bundeslaender:
                data_bundeslaender[str(IdBundesland)] = {
                    "Name": row[data["indexes"]["Bundesland"]],
                    "daten_nach_meldedatum": {},
                    "landkreise": {},
                }

            if (
                not str(Meldedatum)
                in data_bundeslaender[str(IdBundesland)]["daten_nach_meldedatum"]
            ):

                data_bundeslaender[str(IdBundesland)]["daten_nach_meldedatum"][
                    str(Meldedatum)
                ] = {
                    "AnzahlFall": 0,
                    "AnzahlTodesfall": 0,
                    "AnzahlGenesen": 0,
                    "FaellePro100k": 0,  # row[data["indexes"]["FaellePro100k"]],
                    "TodesfaellePro100k": 0,  # row[data["indexes"]["TodesfaellePro100k"]],
                    "Altersgruppe": row[data["indexes"]["Altersgruppe"]],
                }

            # Landkreis

            IdLandkreis = row[data["indexes"]["IdLandkreis"]]

            if (
                not str(IdLandkreis)
                in data_bundeslaender[str(IdBundesland)]["landkreise"]
            ):

                data_bundeslaender[str(IdBundesland)]["landkreise"][
                    str(IdLandkreis)
                ] = {
                    "Name": row[data["indexes"]["Landkreis"]],
                    "Typ": row[data["indexes"]["LandkreisTyp"]],
                    "Bevoelkerung": row[data["indexes"]["Bevoelkerung"]],
                    "daten_nach_meldedatum": {},
                }

            if (
                not str(Meldedatum)
                in data_bundeslaender[str(IdBundesland)]["landkreise"][
                    str(IdLandkreis)
                ]["daten_nach_meldedatum"]
            ):

                data_bundeslaender[str(IdBundesland)]["landkreise"][str(IdLandkreis)][
                    "daten_nach_meldedatum"
                ][str(Meldedatum)] = {
                    # "Bevoelkerung": int(row[data["indexes"]["Bevoelkerung"]]),
                    "AnzahlFall": 0,
                    "AnzahlTodesfall": 0,
                    "AnzahlGenesen": 0,
                    "FaellePro100k": 0,  # row[data["indexes"]["FaellePro100k"]],
                    "TodesfaellePro100k": 0,  # row[data["indexes"]["TodesfaellePro100k"]],
                    "Altersgruppe": row[data["indexes"]["Altersgruppe"]],
                }

            for col_name in ["AnzahlFall", "AnzahlTodesfall", "AnzahlGenesen"]:
                # add to Bundesland
                data_bundeslaender[str(IdBundesland)]["daten_nach_meldedatum"][
                    str(Meldedatum)
                ][col_name] += int(row[int(data["indexes"][col_name])])
                # add to Landkreis
                data_bundeslaender[str(IdBundesland)]["landkreise"][str(IdLandkreis)][
                    "daten_nach_meldedatum"
                ][str(Meldedatum)][col_name] += int(row[int(data["indexes"][col_name])])

        # add Altersgruppen:

        altersgruppe_per_name = {}
        for ag_name in altersgruppen:
            altersgruppe = models.Altersgruppe(Name=ag_name)
            self.session.add(altersgruppe)
            altersgruppe_per_name[ag_name] = altersgruppe
        self.session.commit()

        bundeslaender_per_ID = {}

        # sum up some data
        for IdBundesland in data_bundeslaender:

            # Bundesland

            bundesland = data_bundeslaender[IdBundesland]
            bevoelkerung_bundesland = 0
            for IdLandkreis in bundesland["landkreise"]:
                landkreis = bundesland["landkreise"][IdLandkreis]

                # meldedaten = list(landkreis["daten_nach_meldedatum"])
                # print(meldedaten)

                bevoelkerung_bundesland += int(landkreis["Bevoelkerung"])

            print("Bevoelkerung: " + str(bevoelkerung_bundesland))
            for meldedatum in bundesland["daten_nach_meldedatum"]:

                bundesland["daten_nach_meldedatum"][meldedatum][
                    "FaellePro100k"
                ] = round(
                    bundesland["daten_nach_meldedatum"][meldedatum]["AnzahlFall"]
                    / (bevoelkerung_bundesland / 100000),
                    2,
                )

                bundesland["daten_nach_meldedatum"][meldedatum][
                    "TodesfaellePro100k"
                ] = round(
                    bundesland["daten_nach_meldedatum"][meldedatum]["AnzahlTodesfall"]
                    / (bevoelkerung_bundesland / 100000),
                    2,
                )

            bundesland_sa = models.Bundesland(ID=IdBundesland, Name=bundesland["Name"])

            for meldedatum in bundesland["daten_nach_meldedatum"]:
                d = bundesland["daten_nach_meldedatum"][meldedatum]
                bundesland_daten_nach_meldedatum_sa = (
                    models.Bundesland_Daten_Nach_Meldedatum(
                        MeldeDatum=int(meldedatum),
                        AnzahlFall=d["AnzahlFall"],
                        AnzahlTodesfall=d["AnzahlTodesfall"],
                        AnzahlGenesen=d["AnzahlTodesfall"],
                        Bevoelkerung=d["AnzahlTodesfall"],
                        FaellePro100k=d["AnzahlTodesfall"],
                        TodesfaellePro100k=d["AnzahlTodesfall"],
                        Altersgruppe=altersgruppe_per_name[d["Altersgruppe"]],
                    )
                )
                bundesland_sa.daten_nach_meldedatum.append(
                    bundesland_daten_nach_meldedatum_sa
                )
            self.session.add(bundesland_sa)

            for IdLandkreis in bundesland["landkreise"]:
                landkreis = bundesland["landkreise"][IdLandkreis]
                landkreis_sa = models.Landkreis(
                    Name=landkreis["Name"],
                    Typ=landkreis["Typ"],
                    Bevoelkerung=landkreis["Bevoelkerung"],
                )
                print(landkreis["Name"])

                for meldedatum in landkreis["daten_nach_meldedatum"]:
                    d = landkreis["daten_nach_meldedatum"][meldedatum]
                    landkreis_daten_nach_meldedatum_sa = (
                        models.Landkreis_Daten_Nach_Meldedatum(
                            MeldeDatum=int(meldedatum),
                            AnzahlFall=d["AnzahlFall"],
                            AnzahlTodesfall=d["AnzahlTodesfall"],
                            AnzahlGenesen=d["AnzahlTodesfall"],
                            Bevoelkerung=d["AnzahlTodesfall"],
                            FaellePro100k=d["AnzahlTodesfall"],
                            TodesfaellePro100k=d["AnzahlTodesfall"],
                            Altersgruppe=altersgruppe_per_name[d["Altersgruppe"]],
                        )
                    )
                    landkreis_sa.daten_nach_meldedatum.append(
                        landkreis_daten_nach_meldedatum_sa
                    )

                bundesland_sa.landkreise.append(landkreis_sa)
            self.session.commit()

        # print(data_bundeslaender)

    def create(self, date):

        from sqlalchemy.engine import Engine
        from sqlalchemy import event

        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            # print("event")
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=OFF")
            # cursor.execute("PRAGMA cache_size = 100000")
            cursor.execute("PRAGMA cache_size = -20000")
            cursor.execute("PRAGMA SYNCHRONOUS = OFF")
            cursor.execute("PRAGMA LOCKING_MODE = EXCLUSIVE")
            cursor.close()

        self._clear_db()
        data = read_data_from_csv(
            csv_file_path="downloads/full-data.csv",
            expected_header_line="IdBundesland,Bundesland,Landkreis,Altersgruppe,Geschlecht,AnzahlFall,AnzahlTodesfall,ObjectId,Meldedatum,IdLandkreis,Datenstand,NeuerFall,NeuerTodesfall,Refdatum,NeuGenesen,AnzahlGenesen,IstErkrankungsbeginn,Altersgruppe2,globalID,caseHash,msgHash,RefDay,MeldeDay,LandkreisName,LandkreisTyp,NeuerFallKlar,newBeforeDay,newCaseBeforeDay,RefdatumKlar,MeldedatumKlar,AnzahlFallLfd,AnzahlTodesfallLfd,Bevoelkerung,FaellePro100k,TodesfaellePro100k,isStadt,ErkDay,newCaseOnDay,newOnDay,caseDelay,NeuerTodesfallKlar,newDeathBeforeDay,missingSinceDay,newDeathOnDay,deathDelay,missingCasesInOldRecord,poppedUpOnDay",
        )
        self._insert_bundeslaender_landkreise_altersgruppen(data)
        # self.insert_landkreise_data(full_data)
        # self.insert_faelle_data(full_data)
