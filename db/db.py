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
from datetime import datetime  # , datetime, timedelta

from app import models  # ,crud,  schemas
from app.database import SessionLocal, engine

def read_data_from_csv(csv_file_path: str, header: dict):
    rows = []
    csv_reader = csv.reader(open(csv_file_path, "rt", encoding="utf-8"))
    for row in csv_reader:
        rows.append(row)
    column_names = list(header.keys())
    if rows[0] != column_names:
        raise Exception("Bad Header in " + csv_file_path)
    header_names = rows[0]
    indexes = {}
    for col in column_names:
        indexes[col] = header_names.index(col)
    rows.pop(0)
    indexes_to_int = []
    indexes_to_float = []
    indexes_to_isodate = {

    }

    header_keys = list(header.keys())

    for i in range(0, len(header_keys)):
        if header[header_keys[i]] == "int":
            indexes_to_int.append(i)
        if header[header_keys[i]] == "float":
            indexes_to_float.append(i)

        if type(header[header_keys[i]]) is list:

            if header[header_keys[i]][0] == "date":
                indexes_to_isodate[i] = header[header_keys[i]][1]

    for row_index in range(0, len(rows)):
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

        for i in indexes_to_isodate:
            if row[i] == "":
                row[i] = None
            else:
                mydatetime = datetime.strptime(row[i], indexes_to_isodate[i])
                row[i] = mydatetime.date().isoformat()

        rows[row_index] = row

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

    def _update_bundesrepublik(self, bundesrepublik):
        sa_bundesrepublik = self.session.query(models.Bundesrepublik).one_or_none()
        if sa_bundesrepublik is None:
            sa_bundesrepublik = models.Bundesrepublik(
                ID=1,
                flaeche=bundesrepublik["flaeche"],
                dichte=bundesrepublik["dichte"],
                einwohner=bundesrepublik["einwohner"]
            )
            for d in bundesrepublik["data"]:
                sa_bundesrepublik_data = models.Bundesrepublik_Daten(**d)
                sa_bundesrepublik.daten.append(sa_bundesrepublik_data)
            self.session.add(sa_bundesrepublik)
            self.session.commit()
        else:
            print("To Do : update Bundesrepublik")

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

    def _update_bundeslaender(self, bundeslaender_by_id):
        for bundesland_id in bundeslaender_by_id:
            sa_bundesland = self.session.query(models.Bundesland).filter_by(ID=bundesland_id).one_or_none()
            if sa_bundesland is None:
                bundesland = bundeslaender_by_id[bundesland_id]
                sa_bundesland = models.Bundesland(
                    ID=bundesland_id,
                    BR_ID=1,
                    name=bundesland["name"],
                    flaeche=bundesland["flaeche"],
                    dichte=bundesland["dichte"],
                    einwohner=bundesland["einwohner"]
                )
                for d in bundesland["data"]:
                    sa_bundesland_data = models.Bundesland_Daten(**d)
                    sa_bundesland.daten.append(sa_bundesland_data)
                self.session.add(sa_bundesland)
                self.session.commit()
            else:
                print("To Do : update Bundeslaender")

    def _get_landkreise_data(self, data):
        IdLandkreis_index = data["indexes"]["IdLandkreis"]
        LandkreisTyp_index = data["indexes"]["LandkreisTyp"]
        landkreise_by_id = {}
        for row in data["rows"]:
            if row[LandkreisTyp_index] not in ["BL", "BR"]:
                lk_id = int(row[IdLandkreis_index])
                if lk_id not in landkreise_by_id:
                    landkreise_by_id[lk_id] = {
                        "name": row[data["indexes"]["Landkreis"]],
                        "typ": row[data["indexes"]["LandkreisTyp"]],
                        "flaeche": row[data["indexes"]["Flaeche"]],
                        "einwohner": row[data["indexes"]["Einwohner"]],
                        "dichte": row[data["indexes"]["Dichte"]],
                        "BL_ID": row[data["indexes"]["IdBundesland"]],
                        "data": []
                    }
                landkreise_by_id[lk_id]["data"].append(self._get_row_data(data["indexes"], row))
        return landkreise_by_id

    def _update_landkreise(self, landkreise_by_id):

        for lk_id in landkreise_by_id:

            sa_landkreis = self.session.query(models.Landkreis).filter_by(ID=lk_id).one_or_none()
            if sa_landkreis is None:
                landkreis = landkreise_by_id[lk_id]
                sa_landkreis = models.Landkreis(
                    ID=lk_id,
                    BL_ID=landkreis["BL_ID"],
                    name=landkreis["name"],
                    typ=landkreis["typ"],
                    flaeche=landkreis["flaeche"],
                    dichte=landkreis["dichte"],
                    einwohner=landkreis["einwohner"]
                )
                for d in landkreis["data"]:
                    sa_landkreis_data = models.Landkreis_Daten(**d)
                    sa_landkreis.daten.append(sa_landkreis_data)
                self.session.add(sa_landkreis)

            else:
                print("To Do : update Landkreis")
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
            csv_data = read_data_from_csv(csv_file_path=full_data_file_path, header={
                "DatenstandTag": "int",
                "Datum": ["date", "%d.%m.%Y"],
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
        self._update_bundeslaender(data["bundeslaender"])
        data["landkreise"] = self._get_landkreise_data(csv_data)
        self._update_landkreise(data["landkreise"])
        f = open("data.json", "w")
        # f.write(json.dumps(data))
        f.write(json.dumps(data["landkreise"][1001]))
        data = None
        # self._insert_sorted_data(data)
        # self.insert_landkreise_data(full_data)
        # self.insert_faelle_data(full_data)
