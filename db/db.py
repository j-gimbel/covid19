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

    def _sort_data(self, data):

        sorted_data = {"altersgruppen": [], "bundeslaender_by_id": {}}
        altersgruppen = []

        # first we create the main objects in the tree

        for row in data["rows"]:
            # Altersgruppen
            altersgruppe = row[data["indexes"]["Altersgruppe"]]
            if altersgruppe not in sorted_data["altersgruppen"]:
                sorted_data["altersgruppen"].append(altersgruppe)
            Meldedatum = row[data["indexes"]["Meldedatum"]]

            # Bundesland

            IdBundesland = row[data["indexes"]["IdBundesland"]]
            if not str(IdBundesland) in sorted_data["bundeslaender_by_id"]:
                sorted_data["bundeslaender_by_id"][str(IdBundesland)] = {
                    "Name": row[data["indexes"]["Bundesland"]],
                    "daten_nach_meldedatum": {},
                    "landkreise": {},
                }

            if (
                not str(Meldedatum)
                in sorted_data["bundeslaender_by_id"][str(IdBundesland)][
                    "daten_nach_meldedatum"
                ]
            ):

                sorted_data["bundeslaender_by_id"][str(IdBundesland)][
                    "daten_nach_meldedatum"
                ][str(Meldedatum)] = {
                    "AnzahlFall": 0,
                    "AnzahlTodesfall": 0,
                    "AnzahlGenesen": 0,
                    "AnzahlFallSumme": 0,
                    "AnzahlTodesfallSumme": 0,
                    "AnzahlGenesenSumme": 0,
                    # "FaellePro100k": 0,  # row[data["indexes"]["FaellePro100k"]],
                    # "TodesfaellePro100k": 0,  # row[data["indexes"]["TodesfaellePro100k"]],
                    "Altersgruppe": row[data["indexes"]["Altersgruppe"]],
                }

            # Landkreis

            IdLandkreis = row[data["indexes"]["IdLandkreis"]]

            if (
                not str(IdLandkreis)
                in sorted_data["bundeslaender_by_id"][str(IdBundesland)]["landkreise"]
            ):

                sorted_data["bundeslaender_by_id"][str(IdBundesland)]["landkreise"][
                    str(IdLandkreis)
                ] = {
                    "Name": row[data["indexes"]["Landkreis"]],
                    "Typ": row[data["indexes"]["LandkreisTyp"]],
                    "Bevoelkerung": row[data["indexes"]["Bevoelkerung"]],
                    "daten_nach_meldedatum": {},
                }

            if (
                not str(Meldedatum)
                in sorted_data["bundeslaender_by_id"][str(IdBundesland)]["landkreise"][
                    str(IdLandkreis)
                ]["daten_nach_meldedatum"]
            ):

                sorted_data["bundeslaender_by_id"][str(IdBundesland)]["landkreise"][
                    str(IdLandkreis)
                ]["daten_nach_meldedatum"][str(Meldedatum)] = {
                    # "Bevoelkerung": int(row[data["indexes"]["Bevoelkerung"]]),
                    "AnzahlFall": 0,
                    "AnzahlTodesfall": 0,
                    "AnzahlGenesen": 0,
                    # "FaellePro100k": 0,  # row[data["indexes"]["FaellePro100k"]],
                    # "TodesfaellePro100k": 0,  # row[data["indexes"]["TodesfaellePro100k"]],
                    "Altersgruppe": row[data["indexes"]["Altersgruppe"]],
                }

            for col_name in ["AnzahlFall", "AnzahlTodesfall", "AnzahlGenesen"]:
                # add to Bundesland
                sorted_data["bundeslaender_by_id"][str(IdBundesland)][
                    "daten_nach_meldedatum"
                ][str(Meldedatum)][col_name] += int(row[int(data["indexes"][col_name])])
                # add to Landkreis
                sorted_data["bundeslaender_by_id"][str(IdBundesland)]["landkreise"][
                    str(IdLandkreis)
                ]["daten_nach_meldedatum"][str(Meldedatum)][col_name] += int(
                    row[int(data["indexes"][col_name])]
                )

        # now we accumulate the data

        for IdBundesland in sorted_data["bundeslaender_by_id"]:
            # Bundesland
            bundesland = sorted_data["bundeslaender_by_id"][IdBundesland]

            meldedaten_sorted = sorted(
                list(bundesland["daten_nach_meldedatum"]))
            stop_at_meldedatum = meldedaten_sorted[0]
            next_row_exists = True
            while next_row_exists:
                AnzahlFallSumme = 0
                AnzahlTodesfallSumme = 0
                AnzahlGenesenSumme = 0
                for i in range(0, len(meldedaten_sorted)):
                    AnzahlFallSumme += bundesland["daten_nach_meldedatum"][
                        meldedaten_sorted[i]
                    ]["AnzahlFall"]
                    AnzahlTodesfallSumme += bundesland["daten_nach_meldedatum"][
                        meldedaten_sorted[i]
                    ]["AnzahlTodesfall"]
                    AnzahlGenesenSumme += bundesland["daten_nach_meldedatum"][
                        meldedaten_sorted[i]
                    ]["AnzahlGenesen"]
                    if (meldedaten_sorted[i] == stop_at_meldedatum) or (
                        i == len(meldedaten_sorted) - 1
                    ):
                        bundesland["daten_nach_meldedatum"][meldedaten_sorted[i]][
                            "AnzahlFallSumme"
                        ] = AnzahlFallSumme
                        bundesland["daten_nach_meldedatum"][meldedaten_sorted[i]][
                            "AnzahlTodesfallSumme"
                        ] = AnzahlTodesfallSumme
                        bundesland["daten_nach_meldedatum"][meldedaten_sorted[i]][
                            "AnzahlGenesenSumme"
                        ] = AnzahlGenesenSumme

                        if i == len(meldedaten_sorted) - 1:
                            next_row_exists = False
                            break
                        stop_at_meldedatum = meldedaten_sorted[i + 1]

            bevoelkerung_bundesland = 0
            for IdLandkreis in bundesland["landkreise"]:
                landkreis = bundesland["landkreise"][IdLandkreis]

                # sum up Bevoelkerung d. Bundeslandes
                bevoelkerung_bundesland += int(landkreis["Bevoelkerung"])

                meldedaten_sorted = sorted(
                    list(landkreis["daten_nach_meldedatum"]))
                stop_at_meldedatum = meldedaten_sorted[0]
                next_row_exists = True
                while next_row_exists:
                    AnzahlFallSumme = 0
                    AnzahlTodesfallSumme = 0
                    AnzahlGenesenSumme = 0
                    for i in range(0, len(meldedaten_sorted)):
                        AnzahlFallSumme += landkreis["daten_nach_meldedatum"][
                            meldedaten_sorted[i]
                        ]["AnzahlFall"]
                        AnzahlTodesfallSumme += landkreis["daten_nach_meldedatum"][
                            meldedaten_sorted[i]
                        ]["AnzahlTodesfall"]
                        AnzahlGenesenSumme += landkreis["daten_nach_meldedatum"][
                            meldedaten_sorted[i]
                        ]["AnzahlGenesen"]
                        if (meldedaten_sorted[i] == stop_at_meldedatum) or (
                            i == len(meldedaten_sorted) - 1
                        ):
                            landkreis["daten_nach_meldedatum"][meldedaten_sorted[i]][
                                "AnzahlFallSumme"
                            ] = AnzahlFallSumme
                            landkreis["daten_nach_meldedatum"][meldedaten_sorted[i]][
                                "AnzahlTodesfallSumme"
                            ] = AnzahlTodesfallSumme
                            landkreis["daten_nach_meldedatum"][meldedaten_sorted[i]][
                                "AnzahlGenesenSumme"
                            ] = AnzahlGenesenSumme

                            if i == len(meldedaten_sorted) - 1:
                                next_row_exists = False
                                break
                            stop_at_meldedatum = meldedaten_sorted[i + 1]

                bundesland["landkreise"][IdLandkreis] = landkreis
            bundesland["Bevoelkerung"] = bevoelkerung_bundesland

            sorted_data["bundeslaender_by_id"][str(IdBundesland)] = bundesland

        return sorted_data

    def _insert_sorted_data(self, sorted_data: dict):

        # add Altersgruppen:
        altersgruppe_per_name = {}
        for ag_name in sorted_data["altersgruppen"]:
            altersgruppe = models.Altersgruppe(Name=ag_name)
            self.session.add(altersgruppe)
            altersgruppe_per_name[ag_name] = altersgruppe
        self.session.commit()

        for IdBundesland in sorted_data["bundeslaender_by_id"]:

            bundesland = sorted_data["bundeslaender_by_id"][IdBundesland]
            bundesland_sa = models.Bundesland(
                ID=IdBundesland,
                Name=bundesland["Name"],
                Bevoelkerung=bundesland["Bevoelkerung"],
            )

            meldedaten_sorted = sorted(
                list(bundesland["daten_nach_meldedatum"]))
            # bundesland["daten_nach_meldedatum"]:
            for meldedatum in meldedaten_sorted:

                d = bundesland["daten_nach_meldedatum"][meldedatum]
                bundesland_daten_nach_meldedatum_sa = (
                    models.Bundesland_Daten_Nach_Meldedatum(
                        MeldeDatum=int(meldedatum),
                        AnzahlFall=d["AnzahlFall"],
                        AnzahlTodesfall=d["AnzahlTodesfall"],
                        AnzahlGenesen=d["AnzahlGenesen"],
                        AnzahlFallSumme=d["AnzahlFallSumme"],
                        AnzahlTodesfallSumme=d["AnzahlTodesfallSumme"],
                        AnzahlGenesenSumme=d["AnzahlGenesenSumme"],
                        Altersgruppe=altersgruppe_per_name[d["Altersgruppe"]],
                    )
                )
                bundesland_sa.daten_nach_meldedatum.append(
                    bundesland_daten_nach_meldedatum_sa
                )

            for IdLandkreis in bundesland["landkreise"]:
                landkreis = bundesland["landkreise"][IdLandkreis]

                landkreis_sa = models.Landkreis(
                    Name=landkreis["Name"],
                    Typ=landkreis["Typ"],
                    Bevoelkerung=landkreis["Bevoelkerung"],
                )

                meldedaten_sorted = sorted(
                    list(landkreis["daten_nach_meldedatum"]))
                for (
                    meldedatum
                ) in meldedaten_sorted:  # landkreis["daten_nach_meldedatum"]:
                    d = landkreis["daten_nach_meldedatum"][meldedatum]
                    landkreis_daten_nach_meldedatum_sa = (
                        models.Landkreis_Daten_Nach_Meldedatum(
                            MeldeDatum=int(meldedatum),
                            AnzahlFall=d["AnzahlFall"],
                            AnzahlTodesfall=d["AnzahlTodesfall"],
                            AnzahlGenesen=d["AnzahlGenesen"],
                            AnzahlFallSumme=d["AnzahlFallSumme"],
                            AnzahlTodesfallSumme=d["AnzahlTodesfallSumme"],
                            AnzahlGenesenSumme=d["AnzahlGenesenSumme"],
                            Altersgruppe=altersgruppe_per_name[d["Altersgruppe"]],
                        )
                    )
                    landkreis_sa.daten_nach_meldedatum.append(
                        landkreis_daten_nach_meldedatum_sa
                    )

                bundesland_sa.landkreise.append(landkreis_sa)

            self.session.add(bundesland_sa)
        self.session.commit()

    def create(self, full_data_file_path):

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
            csv_file_path=full_data_file_path,
            expected_header_line="DatenstandTag,AnzahlFall,AnzahlFallNeu,AnzahlTodesfall,AnzahlTodesfallNeu,AnzahlGenesen,AnzahlGenesenNeu,IdLandkreis,Landkreis,IdBundesland,Bundesland,Flaeche,Einwohner,Dichte,InzidenzFallNeu,InzidenzTodesfallNeu,InzidenzFall,InzidenzTodesfall,AnzahlFallNeu-7-Tage,AnzahlFallNeu-7-Tage-Trend,AnzahlFallNeu-7-Tage-7-Tage-davor,AnzahlTodesfallNeu-7-Tage,AnzahlTodesfallNeu-7-Tage-Trend,AnzahlTodesfallNeu-7-Tage-7-Tage-davor,AnzahlGenesenNeu-7-Tage,AnzahlGenesenNeu-7-Tage-Trend,InzidenzFallNeu-7-Tage,InzidenzFallNeu-7-Tage-Trend,InzidenzFallNeu-7-Tage-7-Tage-davor,InzidenzFallNeu-7-Tage-Trend-Spezial,InzidenzFallNeu-7-Tage-R,InzidenzFallNeu-Prognose-1-Wochen,InzidenzFallNeu-Prognose-2-Wochen,InzidenzFallNeu-Prognose-4-Wochen,InzidenzFallNeu-Prognose-8-Wochen,InzidenzFallNeu-Tage-bis-50,InzidenzFallNeu-Tage-bis-100,Kontaktrisiko,InzidenzTodesfallNeu-7-Tage,InzidenzTodesfallNeu-7-Tage-Trend,InzidenzTodesfallNeu-7-Tage-7-Tage-davor,InzidenzTodesfallNeu-7-Tage-Trend-Spezial")
        sorted_data = self._sort_data(data)
        # print(sorted_data)
        f = open("dump.json", "w")

        f.write(json.dumps(sorted_data))
        data = None
        self._insert_sorted_data(sorted_data)
        # self.insert_landkreise_data(full_data)
        # self.insert_faelle_data(full_data)
