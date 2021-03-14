import json
# from sqlalchemy.orm import Session, load_only
import logging
# import requests
import os
import csv
# import shutil
# import gzip
# import glob
# import re
# from datetime import date, datetime, timedelta

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

def read_data_from_csv_new(csv_file_path: str, header: dict):
    rows = []
    csv_reader = csv.reader(open(csv_file_path, "rt", encoding="utf-8"))
    for row in csv_reader:
        rows.append(row)
    column_names = list(header.keys())
    print(column_names)
    if rows[0] != column_names:
        raise Exception("Bad Header in " + csv_file_path)
    header_names = rows[0]
    indexes = {}
    for col in column_names:
        indexes[col] = header_names.index(col)
    rows.pop(0)

    indexes_to_int = []
    indexes_to_float = []

    header_keys = list(header.keys())
    for i in range(0, len(header_keys)):
        if header[header_keys[i]] == "int":
            indexes_to_int.append(i)
        if header[header_keys[i]] == "float":
            indexes_to_float.append(i)
    print(indexes_to_int)

    for row_index in range(0, len(rows)):
        # print(str(row_index))
        row = rows[row_index]
        for i in indexes_to_int:
            if row[i] == "":
                row[i] = None
            else:
                row[i] = int(row[i])

        for i in indexes_to_float:
            if row[i] == "":
                row[i] = None
            else:
                row[i] = float(row[i])
        rows[row_index] = row

    # exit(1)
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

    def _get_agegroups(self, data):

        agegroups = []
        for row in data["rows"]:
            altersgruppe = row[data["indexes"]["Altersgruppe"]]
            if altersgruppe not in agegroups:
                agegroups.append(altersgruppe)
        return agegroups

    def _get_row_data(self, indexes, row):
        data = {}
        for k in ["DatenstandTag", "Datum", "AnzahlFall", "AnzahlFallNeu", "AnzahlTodesfall", "AnzahlTodesfallNeu", "AnzahlGenesen", "AnzahlGenesenNeu", "InzidenzFallNeu", "InzidenzTodesfallNeu", "InzidenzFall", "InzidenzTodesfall", "AnzahlFallNeu_7_Tage", "AnzahlFallNeu_7_Tage_Trend", "AnzahlFallNeu_7_Tage_7_Tage_davor", "AnzahlTodesfallNeu_7_Tage", "AnzahlTodesfallNeu_7_Tage_Trend", "AnzahlTodesfallNeu_7_Tage_7_Tage_davor", "AnzahlGenesenNeu_7_Tage", "AnzahlGenesenNeu_7_Tage_Trend", "InzidenzFallNeu_7_Tage", "InzidenzFallNeu_7_Tage_Trend", "InzidenzFallNeu_7_Tage_7_Tage_davor", "InzidenzFallNeu_7_Tage_Trend_Spezial", "InzidenzFallNeu_7_Tage_R", "InzidenzFallNeu_Prognose_1_Wochen", "InzidenzFallNeu_Prognose_2_Wochen", "InzidenzFallNeu_Prognose_4_Wochen", "InzidenzFallNeu_Prognose_8_Wochen", "InzidenzFallNeu_Tage_bis_50", "InzidenzFallNeu_Tage_bis_100", "Kontaktrisiko", "InzidenzTodesfallNeu_7_Tage", "InzidenzTodesfallNeu_7_Tage_Trend", "InzidenzTodesfallNeu_7_Tage_7_Tage_davor", "InzidenzTodesfallNeu_7_Tage_Trend_Spezial"]:
            data[k] = row[indexes[k.replace("_", "-")]]

        return data

    def _get_bundesrepublik_data(self, data):

        IdLandkreis_index = data["indexes"]["IdLandkreis"]
        bundesrepublik = {'data': []}
        for row in data["rows"]:

            if int(row[IdLandkreis_index]) == 0:
                if "flaeche" not in bundesrepublik:
                    bundesrepublik["flaeche"] = row[data["indexes"]["Flaeche"]]
                    bundesrepublik["einwohner"] = row[data["indexes"]["Einwohner"]]
                    bundesrepublik["dichte"] = row[data["indexes"]["Dichte"]]
                bundesrepublik["data"].append(self._get_row_data(data["indexes"], row))
        return bundesrepublik

    def _get_bundeslaender_data(self, data):
        LandkreisTyp_index = data["indexes"]["LandkreisTyp"]
        IdBundesland_index = data["indexes"]["IdBundesland"]

        bundeslaender_by_id = {}
        for row in data["rows"]:
            if row[LandkreisTyp_index] == "BL":
                bundesland_id = int(row[IdBundesland_index])

                if bundesland_id not in bundeslaender_by_id:
                    bundeslaender_by_id[bundesland_id] = {
                        "name": row[data["indexes"]["Bundesland"]],
                        "flaeche": row[data["indexes"]["Flaeche"]],
                        "einwohner": row[data["indexes"]["Einwohner"]],
                        "dichte": row[data["indexes"]["Dichte"]],
                        "data": []
                    }
                bundeslaender_by_id[bundesland_id]["data"].append(self._get_row_data(data["indexes"], row))

        return bundeslaender_by_id
    """
    def _sort_data(self, with_agegroups, data):
        sorted_data = {}

        if with_agegroups:
            sorted_data["altersgruppen"] = self._get_agegroups(data)

        sorted_data["bundesrepublik"] = self._get_bundesrepublik_data(data)
        sorted_data["bundeslaender"] = self._get_bundeslaender_data(data)

        return sorted_data
    """

    def _update_bundesrepublik(self, bundesrepublik):

        sa_bundesrepublik = self.session.query(models.Bundesrepublik).one_or_none()
        if sa_bundesrepublik is None:
            sa_bundesrepublik = models.Bundesrepublik(
                flaeche=bundesrepublik["flaeche"],
                dichte=bundesrepublik["dichte"],
                einwohner=bundesrepublik["einwohner"]
            )
            for d in bundesrepublik["data"]:
                print(d)
                sa_bundesrepublik_data = models.Bundesrepublik_Daten(
                    **d
                )
                sa_bundesrepublik.daten.append(sa_bundesrepublik_data)

            self.session.add(sa_bundesrepublik)
            self.session.commit()

    def _sort_data_old(self, with_agegroups, data):

        sorted_data = {"altersgruppen": [], "bundeslaender_by_id": {}}
        #altersgruppen = []

        # first we create the main objects in the tree

        for row in data["rows"]:
            # Altersgruppen

            if with_agegroups:
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

    def create(self, with_agegroups: bool, full_data_file_path: str):

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

        if with_agegroups:
            csv_data = read_data_from_csv(csv_file_path=full_data_file_path, expected_header_line="DatenstandTag,Datum,IdLandkreis,Landkreis,LandkreisTyp,IdBundesland,Bundesland,Flaeche,AnzahlFall,AnzahlFallNeu,AnzahlTodesfall,AnzahlTodesfallNeu,AnzahlGenesen,AnzahlGenesenNeu,Einwohner,Dichte,InzidenzFallNeu,InzidenzTodesfallNeu,InzidenzFall,InzidenzTodesfall,AnzahlFallNeu-7-Tage,AnzahlFallNeu-7-Tage-Trend,AnzahlFallNeu-7-Tage-7-Tage-davor,AnzahlTodesfallNeu-7-Tage,AnzahlTodesfallNeu-7-Tage-Trend,AnzahlTodesfallNeu-7-Tage-7-Tage-davor,AnzahlGenesenNeu-7-Tage,AnzahlGenesenNeu-7-Tage-Trend,InzidenzFallNeu-7-Tage,InzidenzFallNeu-7-Tage-Trend,InzidenzFallNeu-7-Tage-7-Tage-davor,InzidenzFallNeu-7-Tage-Trend-Spezial,InzidenzFallNeu-7-Tage-R,InzidenzFallNeu-Prognose-1-Wochen,InzidenzFallNeu-Prognose-2-Wochen,InzidenzFallNeu-Prognose-4-Wochen,InzidenzFallNeu-Prognose-8-Wochen,InzidenzFallNeu-Tage-bis-50,InzidenzFallNeu-Tage-bis-100,Kontaktrisiko,InzidenzTodesfallNeu-7-Tage,InzidenzTodesfallNeu-7-Tage-Trend,InzidenzTodesfallNeu-7-Tage-7-Tage-davor,InzidenzTodesfallNeu-7-Tage-Trend-Spezial")
        else:
            csv_data = read_data_from_csv(csv_file_path=full_data_file_path, expected_header_line="DatenstandTag,Datum,IdLandkreis,Landkreis,LandkreisTyp,IdBundesland,Bundesland,Flaeche,AnzahlFall,AnzahlFallNeu,AnzahlTodesfall,AnzahlTodesfallNeu,AnzahlGenesen,AnzahlGenesenNeu,Einwohner,Dichte,InzidenzFallNeu,InzidenzTodesfallNeu,InzidenzFall,InzidenzTodesfall,AnzahlFallNeu-7-Tage,AnzahlFallNeu-7-Tage-Trend,AnzahlFallNeu-7-Tage-7-Tage-davor,AnzahlTodesfallNeu-7-Tage,AnzahlTodesfallNeu-7-Tage-Trend,AnzahlTodesfallNeu-7-Tage-7-Tage-davor,AnzahlGenesenNeu-7-Tage,AnzahlGenesenNeu-7-Tage-Trend,InzidenzFallNeu-7-Tage,InzidenzFallNeu-7-Tage-Trend,InzidenzFallNeu-7-Tage-7-Tage-davor,InzidenzFallNeu-7-Tage-Trend-Spezial,InzidenzFallNeu-7-Tage-R,InzidenzFallNeu-Prognose-1-Wochen,InzidenzFallNeu-Prognose-2-Wochen,InzidenzFallNeu-Prognose-4-Wochen,InzidenzFallNeu-Prognose-8-Wochen,InzidenzFallNeu-Tage-bis-50,InzidenzFallNeu-Tage-bis-100,Kontaktrisiko,InzidenzTodesfallNeu-7-Tage,InzidenzTodesfallNeu-7-Tage-Trend,InzidenzTodesfallNeu-7-Tage-7-Tage-davor,InzidenzTodesfallNeu-7-Tage-Trend-Spezial")
            csv_data = read_data_from_csv_new(csv_file_path=full_data_file_path, header={
                "DatenstandTag": "int",
                "Datum": "str",
                "IdLandkreis": "int",
                "Landkreis": "str",
                "LandkreisTyp": "str",
                "IdBundesland": "int",
                "Bundesland": "str",
                "Flaeche": "float",
                "AnzahlFall": "int",
                "AnzahlFallNeu": "int",
                "AnzahlTodesfall": "int",
                "AnzahlTodesfallNeu": "int",
                "AnzahlGenesen": "int",
                "AnzahlGenesenNeu": "int",
                "Einwohner": "int",
                "Dichte": "float",
                "InzidenzFallNeu": "float",
                "InzidenzTodesfallNeu": "float",
                "InzidenzFall": "float",
                "InzidenzTodesfall": "float",
                "AnzahlFallNeu-7-Tage": "int",
                "AnzahlFallNeu-7-Tage-Trend": "float",
                "AnzahlFallNeu-7-Tage-7-Tage-davor": "int",
                "AnzahlTodesfallNeu-7-Tage": "int",
                "AnzahlTodesfallNeu-7-Tage-Trend": "float",
                "AnzahlTodesfallNeu-7-Tage-7-Tage-davor": "int",
                "AnzahlGenesenNeu-7-Tage": "int",
                "AnzahlGenesenNeu-7-Tage-Trend": "float",
                "InzidenzFallNeu-7-Tage": "float",
                "InzidenzFallNeu-7-Tage-Trend": "float",
                "InzidenzFallNeu-7-Tage-7-Tage-davor": "float",
                "InzidenzFallNeu-7-Tage-Trend-Spezial": "float",
                "InzidenzFallNeu-7-Tage-R": "float",
                "InzidenzFallNeu-Prognose-1-Wochen": "float",
                "InzidenzFallNeu-Prognose-2-Wochen": "float",
                "InzidenzFallNeu-Prognose-4-Wochen": "float",
                "InzidenzFallNeu-Prognose-8-Wochen": "float",
                "InzidenzFallNeu-Tage-bis-50": "float",
                "InzidenzFallNeu-Tage-bis-100": "float",
                "Kontaktrisiko": "float",
                "InzidenzTodesfallNeu-7-Tage": "float",
                "InzidenzTodesfallNeu-7-Tage-Trend": "float",
                "InzidenzTodesfallNeu-7-Tage-7-Tage-davor": "float",
                "InzidenzTodesfallNeu-7-Tage-Trend-Spezial": "float"
            })

        #data = self._get_data(with_agegroups, data)
        # print(sorted_data)
        data = {}
        if with_agegroups:
            data["altersgruppen"] = self._get_agegroups(csv_data)

        data["bundesrepublik"] = self._get_bundesrepublik_data(csv_data)
        self._update_bundesrepublik(data["bundesrepublik"])
        data["bundeslaender"] = self._get_bundeslaender_data(csv_data)

        f = open("data.json", "w")

        f.write(json.dumps(data))
        data = None
        # self._insert_sorted_data(data)
        # self.insert_landkreise_data(full_data)
        # self.insert_faelle_data(full_data)
