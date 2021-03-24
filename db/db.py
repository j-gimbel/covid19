import os
import json
import logging
import csv

from datetime import datetime  # , datetime, timedelta

from app import models  # ,crud,  schemas
from app.database import SessionLocal, engine

def read_data_from_csv(csv_file_path: str, header: dict):
    print("reading csv...")
    rows = []
    csv_reader = csv.reader(open(csv_file_path, "rt", encoding="utf-8"))
    for row in csv_reader:
        rows.append(row)
    column_names = list(header.keys())
    # if rows[0] != column_names:
    # raise Exception("Bad Header in " + csv_file_path)
    for i in range(0, len(rows[0])):
        if rows[0][i] != column_names[i]:
            print("Diff "+rows[0][i] + " != " + column_names[i])

    header_names = rows[0]
    indexes = {}
    for col in column_names:
        indexes[col] = header_names.index(col)
    rows.pop(0)
    indexes_to_int = []
    indexes_to_float = []
    indexes_to_date = {}

    header_keys = list(header.keys())

    for i in range(0, len(header_keys)):
        if header[header_keys[i]] == "int":
            indexes_to_int.append(i)
        if header[header_keys[i]] == "float":
            indexes_to_float.append(i)
        if type(header[header_keys[i]]) is list:
            if header[header_keys[i]][0] == "date":
                indexes_to_date[i] = header[header_keys[i]][1]

    for row_index in range(0, len(rows)):
        row = rows[row_index]

        for i in indexes_to_int:
            if row[i] == "":
                row[i] = None
            else:
                try:
                    row[i] = int(row[i])
                except ValueError as e:
                    print("Wrong int for: " + header_keys[i]+" : "+str(row[i]))
        for i in indexes_to_float:
            if row[i] == "":
                row[i] = None
            else:
                row[i] = float(row[i])
        for i in indexes_to_date:
            if row[i] == "":
                row[i] = None
            else:
                mydatetime = datetime.strptime(row[i], indexes_to_date[i])
                row[i] = mydatetime.date()
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
        print("clearing DB")
        self.session.close()
        #print(os.path.dirname(__file__) + "/../database.db")
        os.remove(os.path.dirname(__file__) + "/../database.db")
        # print(models.Base.metadata.tables.values())
        # models.Base.metadata.drop_all(bind=engine)
        models.Base.metadata.create_all(bind=engine)
        self.session = SessionLocal()

    def _get_row_data(self, indexes, row):
        data = {}

        for k in list(models.Landkreis_Daten.__table__.columns.keys()):
            if k in ["ID", "Landkreis_ID", "Altersgruppe_ID"]:
                continue
                # data[k] = row[indexes[k.replace("_", "-")]]
            data[k] = row[indexes[k]]

        return data

    def _get_bundesrepublik_data(self, data):

        IdLandkreis_index = data["indexes"]["IdLandkreis"]
        bundesrepublik = {'data': []}
        for row in data["rows"]:
            if int(row[IdLandkreis_index]) == 0:
                print("BR found 0")
                if "Flaeche" not in bundesrepublik:
                    bundesrepublik["Flaeche"] = row[data["indexes"]["Flaeche"]]
                    bundesrepublik["Einwohner"] = row[data["indexes"]["Einwohner"]]
                    bundesrepublik["Einwohner_AG_A00_A04"] = row[data["indexes"]["Einwohner_AG_A00_A04"]]
                    bundesrepublik["Einwohner_AG_A05_A14"] = row[data["indexes"]["Einwohner_AG_A05_A14"]]
                    bundesrepublik["Einwohner_AG_A15_A34"] = row[data["indexes"]["Einwohner_AG_A15_A34"]]
                    bundesrepublik["Einwohner_AG_A35_A59"] = row[data["indexes"]["Einwohner_AG_A35_A59"]]
                    bundesrepublik["Einwohner_AG_A60_A79"] = row[data["indexes"]["Einwohner_AG_A60_A79"]]
                    bundesrepublik["Einwohner_AG_A80Plus"] = row[data["indexes"]["Einwohner_AG_A80Plus"]]
                    # bundesrepublik["Dichte"] = row[data["indexes"]["Dichte"]]
                bundesrepublik["data"].append(self._get_row_data(data["indexes"], row))
        return bundesrepublik

    def __process_bundesrepublik(self, bundesrepublik):
        print("processing Bundesrepublik")
        # sa_bundesrepublik = self.session.query(models.Bundesrepublik).one_or_none()
        # if sa_bundesrepublik is None:
        sa_bundesrepublik = models.Bundesrepublik(
            ID=1,
            Flaeche=bundesrepublik["Flaeche"],
            # Dichte=bundesrepublik["Dichte"],
            Einwohner=bundesrepublik["Einwohner"],
            Einwohner_AG_A00_A04=bundesrepublik["Einwohner_AG_A00_A04"],
            Einwohner_AG_A05_A14=bundesrepublik["Einwohner_AG_A05_A14"],
            Einwohner_AG_A15_A34=bundesrepublik["Einwohner_AG_A15_A34"],
            Einwohner_AG_A35_A59=bundesrepublik["Einwohner_AG_A35_A59"],
            Einwohner_AG_A60_A79=bundesrepublik["Einwohner_AG_A60_A79"],
            Einwohner_AG_A80Plus=bundesrepublik["Einwohner_AG_A80Plus"]
        )
        print(str(len(bundesrepublik["data"])))
        for d in bundesrepublik["data"]:
            sa_bundesrepublik_data = models.Bundesrepublik_Daten(**d)
            sa_bundesrepublik.Daten.append(sa_bundesrepublik_data)
        self.session.add(sa_bundesrepublik)
        self.session.commit()
        # else:
        #    print("To Do : update Bundesrepublik")

    def _get_bundeslaender_data(self, data):
        # LandkreisTyp_index = data["indexes"]["LandkreisTyp"]
        IdBundesland_index = data["indexes"]["IdBundesland"]

        IdLandkreis_index = data["indexes"]["IdLandkreis"]

        kuerzel = {
            "Baden-Württemberg": "BW",
            "Bayern": "BY",
            "Berlin": "BE",
            "Brandenburg": "BB",
            "Bremen": "HB",
            "Hamburg": "HH",
            "Hessen": "HE",
            "Mecklenburg-Vorpommern": "MV",
            "Niedersachsen": "NI",
            "Nordrhein-Westfalen": "NW",
            "Rheinland-Pfalz": "RP",
            "Saarland": "SL",
            "Sachsen": "SN",
            "Sachsen-Anhalt": "ST",
            "Schleswig-Holstein": "SH",
            "Thüringen": "TH"

        }

        bundeslaender_by_id = {}
        for row in data["rows"]:
            # if row[LandkreisTyp_index] == "BL":
            if row[IdLandkreis_index] > 0 and row[IdLandkreis_index] < 1000:
                bundesland_id = int(row[IdBundesland_index])

                if bundesland_id not in bundeslaender_by_id:
                    bundeslaender_by_id[bundesland_id] = {
                        "Name": row[data["indexes"]["Bundesland"]],
                        "Kuerzel": kuerzel[row[data["indexes"]["Bundesland"]]],
                        "Flaeche": row[data["indexes"]["Flaeche"]],
                        "Einwohner": row[data["indexes"]["Einwohner"]],
                        "Einwohner_AG_A00_A04": row[data["indexes"]["Einwohner_AG_A00_A04"]],
                        "Einwohner_AG_A05_A14": row[data["indexes"]["Einwohner_AG_A05_A14"]],
                        "Einwohner_AG_A15_A34": row[data["indexes"]["Einwohner_AG_A15_A34"]],
                        "Einwohner_AG_A35_A59": row[data["indexes"]["Einwohner_AG_A35_A59"]],
                        "Einwohner_AG_A60_A79": row[data["indexes"]["Einwohner_AG_A60_A79"]],
                        "Einwohner_AG_A80Plus": row[data["indexes"]["Einwohner_AG_A80Plus"]],
                        # "Dichte": row[data["indexes"]["Dichte"]],
                        "data": []
                    }
                bundeslaender_by_id[bundesland_id]["data"].append(self._get_row_data(data["indexes"], row))

        return bundeslaender_by_id

    def __process_bundeslaender(self, bundeslaender_by_id):
        print("processing Bundesländer")
        total = 0
        for bundesland_id in bundeslaender_by_id:
            bundesland = bundeslaender_by_id[bundesland_id]
            total += len(bundesland["data"])
        print("Total rows: " + str(total))

        counter = 0
        processed = 0
        for bundesland_id in bundeslaender_by_id:
            # sa_bundesland = self.session.query(models.Bundesland).filter_by(ID=bundesland_id).one_or_none()
            # if sa_bundesland is None:
            bundesland = bundeslaender_by_id[bundesland_id]
            sa_bundesland = models.Bundesland(
                ID=bundesland_id,
                BR_ID=1,
                Name=bundesland["Name"],
                Kuerzel=bundesland["Kuerzel"],
                Flaeche=bundesland["Flaeche"],
                # Dichte=bundesland["Dichte"],
                Einwohner=bundesland["Einwohner"],
                Einwohner_AG_A00_A04=bundesland["Einwohner_AG_A00_A04"],
                Einwohner_AG_A05_A14=bundesland["Einwohner_AG_A05_A14"],
                Einwohner_AG_A15_A34=bundesland["Einwohner_AG_A15_A34"],
                Einwohner_AG_A35_A59=bundesland["Einwohner_AG_A35_A59"],
                Einwohner_AG_A60_A79=bundesland["Einwohner_AG_A60_A79"],
                Einwohner_AG_A80Plus=bundesland["Einwohner_AG_A80Plus"]
            )
            for d in bundesland["data"]:
                sa_bundesland_data = models.Bundesland_Daten(**d)
                sa_bundesland.Daten.append(sa_bundesland_data)

            self.session.add(sa_bundesland)
            counter += len(bundesland["data"])
            if counter > 1000:
                processed += counter
                percent = round(processed/total*100, 2)
                print(str(percent)+"%, "+str(processed)+" / "+str(total))
                self.session.commit()
                counter = 0

            self.session.commit()
        # else:
        #    print("To Do : update Bundeslaender")

    def _get_landkreise_data(self, data):
        IdLandkreis_index = data["indexes"]["IdLandkreis"]
        LandkreisTyp_index = data["indexes"]["LandkreisTyp"]
        landkreise_by_id = {}
        for row in data["rows"]:
            if row[LandkreisTyp_index] not in ["BL", "BR"]:
                lk_id = int(row[IdLandkreis_index])
                if lk_id not in landkreise_by_id:
                    landkreise_by_id[lk_id] = {
                        "Name": row[data["indexes"]["Landkreis"]],
                        "Typ": row[data["indexes"]["LandkreisTyp"]],
                        "Flaeche": row[data["indexes"]["Flaeche"]],
                        "Einwohner": row[data["indexes"]["Einwohner"]],
                        "Einwohner_AG_A00_A04": row[data["indexes"]["Einwohner_AG_A00_A04"]],
                        "Einwohner_AG_A05_A14": row[data["indexes"]["Einwohner_AG_A05_A14"]],
                        "Einwohner_AG_A15_A34": row[data["indexes"]["Einwohner_AG_A15_A34"]],
                        "Einwohner_AG_A35_A59": row[data["indexes"]["Einwohner_AG_A35_A59"]],
                        "Einwohner_AG_A60_A79": row[data["indexes"]["Einwohner_AG_A60_A79"]],
                        "Einwohner_AG_A80Plus": row[data["indexes"]["Einwohner_AG_A80Plus"]],
                        # "Dichte": row[data["indexes"]["Dichte"]],
                        "BL_ID": row[data["indexes"]["IdBundesland"]],
                        "data": []
                    }
                landkreise_by_id[lk_id]["data"].append(self._get_row_data(data["indexes"], row))
        return landkreise_by_id

    def __process_landkreise(self, landkreise_by_id):
        print(" processing Landkreise")

        total = 0
        for lk_id in landkreise_by_id:
            landkreis = landkreise_by_id[lk_id]
            total += len(landkreis["data"])
        print("Total rows: "+str(total))
        counter = 0
        processed = 0
        for lk_id in landkreise_by_id:

            sa_landkreis = self.session.query(models.Landkreis).filter_by(ID=lk_id).one_or_none()
            if sa_landkreis is None:
                landkreis = landkreise_by_id[lk_id]
                sa_landkreis = models.Landkreis(
                    ID=lk_id,
                    BL_ID=landkreis["BL_ID"],
                    Name=landkreis["Name"],
                    Typ=landkreis["Typ"],
                    Flaeche=landkreis["Flaeche"],
                    # Dichte=landkreis["Dichte"],
                    Einwohner=landkreis["Einwohner"],
                    Einwohner_AG_A00_A04=landkreis["Einwohner_AG_A00_A04"],
                    Einwohner_AG_A05_A14=landkreis["Einwohner_AG_A05_A14"],
                    Einwohner_AG_A15_A34=landkreis["Einwohner_AG_A15_A34"],
                    Einwohner_AG_A35_A59=landkreis["Einwohner_AG_A35_A59"],
                    Einwohner_AG_A60_A79=landkreis["Einwohner_AG_A60_A79"],
                    Einwohner_AG_A80Plus=landkreis["Einwohner_AG_A80Plus"]
                )
                for d in landkreis["data"]:
                    sa_landkreis_data = models.Landkreis_Daten(**d)
                    sa_landkreis.Daten.append(sa_landkreis_data)

                self.session.add(sa_landkreis)
                counter += len(landkreis["data"])
                if counter > 1000:
                    processed += counter
                    percent = round(processed/total*100, 2)
                    print(str(percent)+"%, "+str(processed)+" / "+str(total))
                    self.session.commit()
                    counter = 0
            else:
                print("To Do : update Landkreis")
            self.session.commit()

    def create(self, no_agegroups: bool, full_data_file_path: str):

        from sqlalchemy.engine import Engine
        from sqlalchemy import event

        @ event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            # print("event")
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=OFF")
            # cursor.execute("PRAGMA cache_size = 100000")
            #cursor.execute("PRAGMA cache_size = -20000")
            cursor.execute("PRAGMA SYNCHRONOUS = OFF")
            cursor.execute("PRAGMA LOCKING_MODE = EXCLUSIVE")
            cursor.close()

        self._clear_db()

        if no_agegroups == False:
            csv_data = read_data_from_csv(csv_file_path=full_data_file_path,
                                          header={
                                              "DatenstandTag": "int",
                                              "Datum": ["date", "%d.%m.%Y"],
                                              "IdLandkreis": "int",
                                              "Landkreis": "str",
                                              "LandkreisTyp": "str",
                                              "IdBundesland": "int",
                                              "Bundesland": "str",
                                              "Flaeche": "float",
                                              "MeldeTag_AnzahlFallNeu": "int",
                                              "MeldeTag_AnzahlFall": "int",
                                              "MeldeTag_AnzahlTodesfallNeu": "int",
                                              "MeldeTag_AnzahlTodesfall": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFall": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfall": "int",
                                              "AnzahlFall": "int",
                                              "AnzahlFallNeu": "int",
                                              "AnzahlTodesfall": "int",
                                              "AnzahlTodesfallNeu": "int",
                                              "AnzahlGenesen": "int",
                                              "AnzahlGenesenNeu": "int",
                                              "PublikationsdauerFallNeu_Min": "int",
                                              "PublikationsdauerFallNeu_Max": "int",
                                              "PublikationsdauerFallNeu_Schnitt": "float",
                                              "PublikationsdauerFallNeu_Median": "float",
                                              "PublikationsdauerFallNeu_StdAbw": "float",
                                              "PublikationsdauerFallNeu_Fallbasis": "int",
                                              "DatenstandTag_Max": "int",

                                              "MeldeTag_AnzahlFallNeu_AG_A00_A04": "int",
                                              "MeldeTag_AnzahlFall_AG_A00_A04": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A00_A04": "int",
                                              "MeldeTag_AnzahlTodesfall_AG_A00_A04": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A00_A04": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFall_AG_A00_A04": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A00_A04": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfall_AG_A00_A04": "int",
                                              "AnzahlFall_AG_A00_A04": "int",
                                              "AnzahlFallNeu_AG_A00_A04": "int",
                                              "AnzahlTodesfall_AG_A00_A04": "int",
                                              "AnzahlTodesfallNeu_AG_A00_A04": "int",
                                              "MeldeTag_AnzahlFallNeu_AG_A05_A14": "int",
                                              "MeldeTag_AnzahlFall_AG_A05_A14": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A05_A14": "int",
                                              "MeldeTag_AnzahlTodesfall_AG_A05_A14": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A05_A14": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFall_AG_A05_A14": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A05_A14": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfall_AG_A05_A14": "int",
                                              "AnzahlFall_AG_A05_A14": "int",
                                              "AnzahlFallNeu_AG_A05_A14": "int",
                                              "AnzahlTodesfall_AG_A05_A14": "int",
                                              "AnzahlTodesfallNeu_AG_A05_A14": "int",
                                              "MeldeTag_AnzahlFallNeu_AG_A15_A34": "int",
                                              "MeldeTag_AnzahlFall_AG_A15_A34": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A15_A34": "int",
                                              "MeldeTag_AnzahlTodesfall_AG_A15_A34": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A15_A34": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFall_AG_A15_A34": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A15_A34": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfall_AG_A15_A34": "int",
                                              "AnzahlFall_AG_A15_A34": "int",
                                              "AnzahlFallNeu_AG_A15_A34": "int",
                                              "AnzahlTodesfall_AG_A15_A34": "int",
                                              "AnzahlTodesfallNeu_AG_A15_A34": "int",
                                              "MeldeTag_AnzahlFallNeu_AG_A35_A59": "int",
                                              "MeldeTag_AnzahlFall_AG_A35_A59": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A35_A59": "int",
                                              "MeldeTag_AnzahlTodesfall_AG_A35_A59": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A35_A59": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFall_AG_A35_A59": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A35_A59": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfall_AG_A35_A59": "int",
                                              "AnzahlFall_AG_A35_A59": "int",
                                              "AnzahlFallNeu_AG_A35_A59": "int",
                                              "AnzahlTodesfall_AG_A35_A59": "int",
                                              "AnzahlTodesfallNeu_AG_A35_A59": "int",
                                              "MeldeTag_AnzahlFallNeu_AG_A60_A79": "int",
                                              "MeldeTag_AnzahlFall_AG_A60_A79": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A60_A79": "int",
                                              "MeldeTag_AnzahlTodesfall_AG_A60_A79": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A60_A79": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFall_AG_A60_A79": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A60_A79": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfall_AG_A60_A79": "int",
                                              "AnzahlFall_AG_A60_A79": "int",
                                              "AnzahlFallNeu_AG_A60_A79": "int",
                                              "AnzahlTodesfall_AG_A60_A79": "int",
                                              "AnzahlTodesfallNeu_AG_A60_A79": "int",
                                              "MeldeTag_AnzahlFallNeu_AG_A80Plus": "int",
                                              "MeldeTag_AnzahlFall_AG_A80Plus": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A80Plus": "int",
                                              "MeldeTag_AnzahlTodesfall_AG_A80Plus": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A80Plus": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFall_AG_A80Plus": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A80Plus": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfall_AG_A80Plus": "int",

                                              "AnzahlFall_AG_A80Plus": "int",
                                              "AnzahlFallNeu_AG_A80Plus": "int",
                                              "AnzahlTodesfall_AG_A80Plus": "int",
                                              "AnzahlTodesfallNeu_AG_A80Plus": "int",

                                              "Einwohner": "int",
                                              "InzidenzFallNeu": "float",

                                              "Einwohner_AG_A00_A04": "int",
                                              "InzidenzFallNeu_AG_A00_A04": "float",
                                              "Einwohner_AG_A05_A14": "int",
                                              "InzidenzFallNeu_AG_A05_A14": "float",
                                              "Einwohner_AG_A15_A34": "int",
                                              "InzidenzFallNeu_AG_A15_A34": "float",
                                              "Einwohner_AG_A35_A59": "int",
                                              "InzidenzFallNeu_AG_A35_A59": "float",
                                              "Einwohner_AG_A60_A79": "int",
                                              "InzidenzFallNeu_AG_A60_A79": "float",
                                              "Einwohner_AG_A80Plus": "int",
                                              "InzidenzFallNeu_AG_A80Plus": "float",

                                              "MeldeTag_AnzahlFallNeu_Gestern": "int",
                                              "MeldeTag_AnzahlFall_Gestern": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_Gestern": "int",
                                              "MeldeTag_AnzahlTodesfall_Gestern": "int",

                                              "MeldeTag_AnzahlFallNeu_AG_A00_A04_Gestern": "int",
                                              "MeldeTag_AnzahlFall_AG_A00_A04_Gestern": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A00_A04_Gestern": "int",
                                              "MeldeTag_AnzahlTodesfall_AG_A00_A04_Gestern": "int",
                                              "MeldeTag_AnzahlFallNeu_AG_A05_A14_Gestern": "int",
                                              "MeldeTag_AnzahlFall_AG_A05_A14_Gestern": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A05_A14_Gestern": "int",
                                              "MeldeTag_AnzahlTodesfall_AG_A05_A14_Gestern": "int",
                                              "MeldeTag_AnzahlFallNeu_AG_A15_A34_Gestern": "int",
                                              "MeldeTag_AnzahlFall_AG_A15_A34_Gestern": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A15_A34_Gestern": "int",
                                              "MeldeTag_AnzahlTodesfall_AG_A15_A34_Gestern": "int",
                                              "MeldeTag_AnzahlFallNeu_AG_A35_A59_Gestern": "int",
                                              "MeldeTag_AnzahlFall_AG_A35_A59_Gestern": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A35_A59_Gestern": "int",
                                              "MeldeTag_AnzahlTodesfall_AG_A35_A59_Gestern": "int",
                                              "MeldeTag_AnzahlFallNeu_AG_A60_A79_Gestern": "int",
                                              "MeldeTag_AnzahlFall_AG_A60_A79_Gestern": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A60_A79_Gestern": "int",
                                              "MeldeTag_AnzahlTodesfall_AG_A60_A79_Gestern": "int",
                                              "MeldeTag_AnzahlFallNeu_AG_A80Plus_Gestern": "int",
                                              "MeldeTag_AnzahlFall_AG_A80Plus_Gestern": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A80Plus_Gestern": "int",
                                              "MeldeTag_AnzahlTodesfall_AG_A80Plus_Gestern": "int",

                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFall_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfall_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A00_A04_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFall_AG_A00_A04_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A00_A04_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfall_AG_A00_A04_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A05_A14_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFall_AG_A05_A14_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A05_A14_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfall_AG_A05_A14_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A15_A34_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFall_AG_A15_A34_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A15_A34_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfall_AG_A15_A34_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A35_A59_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFall_AG_A35_A59_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A35_A59_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfall_AG_A35_A59_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A60_A79_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFall_AG_A60_A79_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A60_A79_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfall_AG_A60_A79_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A80Plus_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFall_AG_A80Plus_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A80Plus_Vor8Tagen": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfall_AG_A80Plus_Vor8Tagen": "int",

                                              "InzidenzTodesfallNeu": "float",
                                              "MeldeTag_InzidenzFall": "float",
                                              "MeldeTag_InzidenzTodesfall": "float",
                                              "MeldeTag_Fallsterblichkeit_Prozent": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzFall": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzTodesfall": "float",
                                              "MeldeTag_Vor7Tagen_Fallsterblichkeit_Prozent": "float",
                                              "InzidenzFall": "float",
                                              "InzidenzTodesfall": "float",
                                              "Fallsterblichkeit_Prozent": "float",

                                              "MeldeTag_InzidenzFall_AG_A00_A04": "float",
                                              "MeldeTag_InzidenzTodesfall_AG_A00_A04": "float",
                                              "MeldeTag_Fallsterblichkeit_Prozent_AG_A00_A04": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzFall_AG_A00_A04": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzTodesfall_AG_A00_A04": "float",
                                              "MeldeTag_Vor7Tagen_Fallsterblichkeit_Prozent_AG_A00_A04": "float",
                                              "InzidenzFall_AG_A00_A04": "float",
                                              "InzidenzTodesfall_AG_A00_A04": "float",
                                              "Fallsterblichkeit_Prozent_AG_A00_A04": "float",
                                              "MeldeTag_InzidenzFall_AG_A05_A14": "float",
                                              "MeldeTag_InzidenzTodesfall_AG_A05_A14": "float",
                                              "MeldeTag_Fallsterblichkeit_Prozent_AG_A05_A14": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzFall_AG_A05_A14": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzTodesfall_AG_A05_A14": "float",
                                              "MeldeTag_Vor7Tagen_Fallsterblichkeit_Prozent_AG_A05_A14": "float",
                                              "InzidenzFall_AG_A05_A14": "float",
                                              "InzidenzTodesfall_AG_A05_A14": "float",
                                              "Fallsterblichkeit_Prozent_AG_A05_A14": "float",
                                              "MeldeTag_InzidenzFall_AG_A15_A34": "float",
                                              "MeldeTag_InzidenzTodesfall_AG_A15_A34": "float",
                                              "MeldeTag_Fallsterblichkeit_Prozent_AG_A15_A34": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzFall_AG_A15_A34": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzTodesfall_AG_A15_A34": "float",
                                              "MeldeTag_Vor7Tagen_Fallsterblichkeit_Prozent_AG_A15_A34": "float",
                                              "InzidenzFall_AG_A15_A34": "float",
                                              "InzidenzTodesfall_AG_A15_A34": "float",
                                              "Fallsterblichkeit_Prozent_AG_A15_A34": "float",
                                              "MeldeTag_InzidenzFall_AG_A35_A59": "float",
                                              "MeldeTag_InzidenzTodesfall_AG_A35_A59": "float",
                                              "MeldeTag_Fallsterblichkeit_Prozent_AG_A35_A59": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzFall_AG_A35_A59": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzTodesfall_AG_A35_A59": "float",
                                              "MeldeTag_Vor7Tagen_Fallsterblichkeit_Prozent_AG_A35_A59": "float",
                                              "InzidenzFall_AG_A35_A59": "float",
                                              "InzidenzTodesfall_AG_A35_A59": "float",
                                              "Fallsterblichkeit_Prozent_AG_A35_A59": "float",
                                              "MeldeTag_InzidenzFall_AG_A60_A79": "float",
                                              "MeldeTag_InzidenzTodesfall_AG_A60_A79": "float",
                                              "MeldeTag_Fallsterblichkeit_Prozent_AG_A60_A79": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzFall_AG_A60_A79": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzTodesfall_AG_A60_A79": "float",
                                              "MeldeTag_Vor7Tagen_Fallsterblichkeit_Prozent_AG_A60_A79": "float",
                                              "InzidenzFall_AG_A60_A79": "float",
                                              "InzidenzTodesfall_AG_A60_A79": "float",
                                              "Fallsterblichkeit_Prozent_AG_A60_A79": "float",
                                              "MeldeTag_InzidenzFall_AG_A80Plus": "float",
                                              "MeldeTag_InzidenzTodesfall_AG_A80Plus": "float",
                                              "MeldeTag_Fallsterblichkeit_Prozent_AG_A80Plus": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzFall_AG_A80Plus": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzTodesfall_AG_A80Plus": "float",
                                              "MeldeTag_Vor7Tagen_Fallsterblichkeit_Prozent_AG_A80Plus": "float",
                                              "InzidenzFall_AG_A80Plus": "float",
                                              "InzidenzTodesfall_AG_A80Plus": "float",
                                              "Fallsterblichkeit_Prozent_AG_A80Plus": "float",

                                              "MeldeTag_InzidenzFall_Gestern": "float",
                                              "MeldeTag_InzidenzTodesfall_Gestern": "float",
                                              "MeldeTag_Fallsterblichkeit_Prozent_Gestern": "float",

                                              "MeldeTag_InzidenzFall_AG_A00_A04_Gestern": "float",
                                              "MeldeTag_InzidenzTodesfall_AG_A00_A04_Gestern": "float",
                                              "MeldeTag_Fallsterblichkeit_Prozent_AG_A00_A04_Gestern": "float",
                                              "MeldeTag_InzidenzFall_AG_A05_A14_Gestern": "float",
                                              "MeldeTag_InzidenzTodesfall_AG_A05_A14_Gestern": "float",
                                              "MeldeTag_Fallsterblichkeit_Prozent_AG_A05_A14_Gestern": "float",
                                              "MeldeTag_InzidenzFall_AG_A15_A34_Gestern": "float",
                                              "MeldeTag_InzidenzTodesfall_AG_A15_A34_Gestern": "float",
                                              "MeldeTag_Fallsterblichkeit_Prozent_AG_A15_A34_Gestern": "float",
                                              "MeldeTag_InzidenzFall_AG_A35_A59_Gestern": "float",
                                              "MeldeTag_InzidenzTodesfall_AG_A35_A59_Gestern": "float",
                                              "MeldeTag_Fallsterblichkeit_Prozent_AG_A35_A59_Gestern": "float",
                                              "MeldeTag_InzidenzFall_AG_A60_A79_Gestern": "float",
                                              "MeldeTag_InzidenzTodesfall_AG_A60_A79_Gestern": "float",
                                              "MeldeTag_Fallsterblichkeit_Prozent_AG_A60_A79_Gestern": "float",
                                              "MeldeTag_InzidenzFall_AG_A80Plus_Gestern": "float",
                                              "MeldeTag_InzidenzTodesfall_AG_A80Plus_Gestern": "float",
                                              "MeldeTag_Fallsterblichkeit_Prozent_AG_A80Plus_Gestern": "float",

                                              "MeldeTag_Vor7Tagen_InzidenzFall_Vor8Tagen": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzTodesfall_Vor8Tagen": "float",
                                              "MeldeTag_Vor7Tagen_Fallsterblichkeit_Prozent_Vor8Tagen": "float",

                                              "MeldeTag_Vor7Tagen_InzidenzFall_AG_A00_A04_Vor8Tagen": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzTodesfall_AG_A00_A04_Vor8Tagen": "float",
                                              "MeldeTag_Vor7Tagen_Fallsterblichkeit_Prozent_AG_A00_A04_Vor8Tagen": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzFall_AG_A05_A14_Vor8Tagen": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzTodesfall_AG_A05_A14_Vor8Tagen": "float",
                                              "MeldeTag_Vor7Tagen_Fallsterblichkeit_Prozent_AG_A05_A14_Vor8Tagen": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzFall_AG_A15_A34_Vor8Tagen": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzTodesfall_AG_A15_A34_Vor8Tagen": "float",
                                              "MeldeTag_Vor7Tagen_Fallsterblichkeit_Prozent_AG_A15_A34_Vor8Tagen": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzFall_AG_A35_A59_Vor8Tagen": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzTodesfall_AG_A35_A59_Vor8Tagen": "float",
                                              "MeldeTag_Vor7Tagen_Fallsterblichkeit_Prozent_AG_A35_A59_Vor8Tagen": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzFall_AG_A60_A79_Vor8Tagen": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzTodesfall_AG_A60_A79_Vor8Tagen": "float",
                                              "MeldeTag_Vor7Tagen_Fallsterblichkeit_Prozent_AG_A60_A79_Vor8Tagen": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzFall_AG_A80Plus_Vor8Tagen": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzTodesfall_AG_A80Plus_Vor8Tagen": "float",
                                              "MeldeTag_Vor7Tagen_Fallsterblichkeit_Prozent_AG_A80Plus_Vor8Tagen": "float",

                                              "MeldeTag_AnzahlFallNeu_7TageSumme": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_7TageSumme": "int",
                                              "AnzahlFallNeu_7TageSumme": "int",
                                              "AnzahlFallNeu_7TageSumme_Trend": "float",
                                              "AnzahlFallNeu_7TageSumme_7_Tage_davor": "int",
                                              "AnzahlTodesfallNeu_7TageSumme": "int",
                                              "AnzahlTodesfallNeu_7TageSumme_Trend": "float",
                                              "AnzahlTodesfallNeu_7TageSumme_7_Tage_davor": "int",
                                              "AnzahlGenesenNeu_7TageSumme": "int",
                                              "AnzahlGenesenNeu_7TageSumme_Trend": "float",

                                              "MeldeTag_AnzahlFallNeu_AG_A00_A04_7TageSumme": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A00_A04_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A00_A04_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A00_A04_7TageSumme": "int",
                                              "AnzahlFallNeu_AG_A00_A04_7TageSumme": "int",
                                              "AnzahlFallNeu_AG_A00_A04_7TageSumme_Trend": "float",
                                              "AnzahlTodesfallNeu_AG_A00_A04_7TageSumme": "int",
                                              "AnzahlTodesfallNeu_AG_A00_A04_7TageSumme_Trend": "float",
                                              "MeldeTag_AnzahlFallNeu_AG_A05_A14_7TageSumme": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A05_A14_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A05_A14_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A05_A14_7TageSumme": "int",
                                              "AnzahlFallNeu_AG_A05_A14_7TageSumme": "int",
                                              "AnzahlFallNeu_AG_A05_A14_7TageSumme_Trend": "float",
                                              "AnzahlTodesfallNeu_AG_A05_A14_7TageSumme": "int",
                                              "AnzahlTodesfallNeu_AG_A05_A14_7TageSumme_Trend": "float",
                                              "MeldeTag_AnzahlFallNeu_AG_A15_A34_7TageSumme": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A15_A34_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A15_A34_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A15_A34_7TageSumme": "int",
                                              "AnzahlFallNeu_AG_A15_A34_7TageSumme": "int",
                                              "AnzahlFallNeu_AG_A15_A34_7TageSumme_Trend": "float",
                                              "AnzahlTodesfallNeu_AG_A15_A34_7TageSumme": "int",
                                              "AnzahlTodesfallNeu_AG_A15_A34_7TageSumme_Trend": "float",
                                              "MeldeTag_AnzahlFallNeu_AG_A35_A59_7TageSumme": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A35_A59_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A35_A59_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A35_A59_7TageSumme": "int",
                                              "AnzahlFallNeu_AG_A35_A59_7TageSumme": "int",
                                              "AnzahlFallNeu_AG_A35_A59_7TageSumme_Trend": "float",
                                              "AnzahlTodesfallNeu_AG_A35_A59_7TageSumme": "int",
                                              "AnzahlTodesfallNeu_AG_A35_A59_7TageSumme_Trend": "float",
                                              "MeldeTag_AnzahlFallNeu_AG_A60_A79_7TageSumme": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A60_A79_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A60_A79_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A60_A79_7TageSumme": "int",
                                              "AnzahlFallNeu_AG_A60_A79_7TageSumme": "int",
                                              "AnzahlFallNeu_AG_A60_A79_7TageSumme_Trend": "float",
                                              "AnzahlTodesfallNeu_AG_A60_A79_7TageSumme": "int",
                                              "AnzahlTodesfallNeu_AG_A60_A79_7TageSumme_Trend": "float",
                                              "MeldeTag_AnzahlFallNeu_AG_A80Plus_7TageSumme": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A80Plus_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A80Plus_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A80Plus_7TageSumme": "int",
                                              "AnzahlFallNeu_AG_A80Plus_7TageSumme": "int",
                                              "AnzahlFallNeu_AG_A80Plus_7TageSumme_Trend": "float",
                                              "AnzahlTodesfallNeu_AG_A80Plus_7TageSumme": "int",
                                              "AnzahlTodesfallNeu_AG_A80Plus_7TageSumme_Trend": "float",

                                              "InzidenzFallNeu_7TageSumme": "float",
                                              "InzidenzFallNeu_7TageSumme_Trend": "float",
                                              "InzidenzFallNeu_7TageSumme_7_Tage_davor": "float",
                                              "InzidenzFallNeu_7TageSumme_Trend_Spezial": "float",
                                              "InzidenzFallNeu_7TageSumme_R": "float",
                                              "InzidenzFallNeu_Prognose_1_Wochen": "float",
                                              "InzidenzFallNeu_Prognose_2_Wochen": "float",
                                              "InzidenzFallNeu_Prognose_4_Wochen": "float",
                                              "InzidenzFallNeu_Prognose_8_Wochen": "float",
                                              "InzidenzFallNeu_Tage_bis_50": "float",
                                              "InzidenzFallNeu_Tage_bis_100": "float",
                                              "Kontaktrisiko": "float",

                                              "InzidenzFallNeu_AG_A00_A04_7TageSumme": "float",
                                              "InzidenzFallNeu_AG_A00_A04_7TageSumme_Trend": "float",
                                              "InzidenzFallNeu_AG_A05_A14_7TageSumme": "float",
                                              "InzidenzFallNeu_AG_A05_A14_7TageSumme_Trend": "float",
                                              "InzidenzFallNeu_AG_A15_A34_7TageSumme": "float",
                                              "InzidenzFallNeu_AG_A15_A34_7TageSumme_Trend": "float",
                                              "InzidenzFallNeu_AG_A35_A59_7TageSumme": "float",
                                              "InzidenzFallNeu_AG_A35_A59_7TageSumme_Trend": "float",
                                              "InzidenzFallNeu_AG_A60_A79_7TageSumme": "float",
                                              "InzidenzFallNeu_AG_A60_A79_7TageSumme_Trend": "float",
                                              "InzidenzFallNeu_AG_A80Plus_7TageSumme": "float",
                                              "InzidenzFallNeu_AG_A80Plus_7TageSumme_Trend": "float",

                                              "MeldeTag_AnzahlFallNeu_Gestern_7TageSumme": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_Gestern_7TageSumme": "int",

                                              "MeldeTag_AnzahlFallNeu_AG_A00_A04_Gestern_7TageSumme": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A00_A04_Gestern_7TageSumme": "int",
                                              "MeldeTag_AnzahlFallNeu_AG_A05_A14_Gestern_7TageSumme": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A05_A14_Gestern_7TageSumme": "int",
                                              "MeldeTag_AnzahlFallNeu_AG_A15_A34_Gestern_7TageSumme": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A15_A34_Gestern_7TageSumme": "int",
                                              "MeldeTag_AnzahlFallNeu_AG_A35_A59_Gestern_7TageSumme": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A35_A59_Gestern_7TageSumme": "int",
                                              "MeldeTag_AnzahlFallNeu_AG_A60_A79_Gestern_7TageSumme": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A60_A79_Gestern_7TageSumme": "int",
                                              "MeldeTag_AnzahlFallNeu_AG_A80Plus_Gestern_7TageSumme": "int",
                                              "MeldeTag_AnzahlTodesfallNeu_AG_A80Plus_Gestern_7TageSumme": "int",

                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_Vor8Tagen_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_Vor8Tagen_7TageSumme": "int",

                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A00_A04_Vor8Tagen_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A00_A04_Vor8Tagen_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A05_A14_Vor8Tagen_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A05_A14_Vor8Tagen_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A15_A34_Vor8Tagen_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A15_A34_Vor8Tagen_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A35_A59_Vor8Tagen_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A35_A59_Vor8Tagen_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A60_A79_Vor8Tagen_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A60_A79_Vor8Tagen_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlFallNeu_AG_A80Plus_Vor8Tagen_7TageSumme": "int",
                                              "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_AG_A80Plus_Vor8Tagen_7TageSumme": "int",
                                              "InzidenzTodesfallNeu_7TageSumme": "float",
                                              "InzidenzTodesfallNeu_7TageSumme_Trend": "float",
                                              "InzidenzTodesfallNeu_7TageSumme_7_Tage_davor": "float",
                                              "InzidenzTodesfallNeu_7TageSumme_Trend_Spezial": "float",
                                              "DatenstandTag_Diff": "int",
                                              "MeldeTag_InzidenzFallNeu_Gestern_7TageSumme": "float",
                                              "AnzahlFallNeu_7TageSumme_Dropped": "int",
                                              "ProzentFallNeu_7TageSumme_Dropped": "float",
                                              "MeldeTag_Vor7Tagen_InzidenzFallNeu_Vor8Tagen_7TageSumme": "float",
                                              "MeldeTag_InzidenzFallNeu_Trend": "float",
                                              "MeldeTag_InzidenzFallNeu_R": "float",
                                              "MeldeTag_InzidenzFallNeu_Prognose_4_Wochen": "float",
                                              "PublikationsdauerFallNeu_Min_Neg": "int",
                                          })
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
                "MeldeTag_AnzahlFallNeu": "int",
                "MeldeTag_AnzahlFall": "int",
                "MeldeTag_AnzahlTodesfallNeu": "int",
                "MeldeTag_AnzahlTodesfall": "int",
                "MeldeTag_Vor7Tagen_AnzahlFallNeu": "int",
                "MeldeTag_Vor7Tagen_AnzahlFall": "int",
                "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu": "int",
                "MeldeTag_Vor7Tagen_AnzahlTodesfall": "int",
                "AnzahlFall": "int",
                "AnzahlFallNeu": "int",
                "AnzahlTodesfall": "int",
                "AnzahlTodesfallNeu": "int",
                "AnzahlGenesen": "int",
                "AnzahlGenesenNeu": "int",
                "PublikationsdauerFallNeu_Min": "int",
                "PublikationsdauerFallNeu_Max": "int",
                "PublikationsdauerFallNeu_Schnitt": "float",
                "PublikationsdauerFallNeu_Median": "float",
                "PublikationsdauerFallNeu_StdAbw": "float",
                "PublikationsdauerFallNeu_Fallbasis": "int",
                "DatenstandTag_Max": "int",
                "Einwohner": "int",
                "Dichte": "float",
                "InzidenzFallNeu": "float",
                "MeldeTag_AnzahlFallNeu_Gestern": "int",
                "MeldeTag_AnzahlFall_Gestern": "int",
                "MeldeTag_AnzahlTodesfallNeu_Gestern": "int",
                "MeldeTag_AnzahlTodesfall_Gestern": "int",
                "MeldeTag_Vor7Tagen_AnzahlFallNeu_Vor8Tagen": "int",
                "MeldeTag_Vor7Tagen_AnzahlFall_Vor8Tagen": "int",
                "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_Vor8Tagen": "int",
                "MeldeTag_Vor7Tagen_AnzahlTodesfall_Vor8Tagen": "int",
                "InzidenzTodesfallNeu": "float",
                "MeldeTag_InzidenzFall": "float",
                "MeldeTag_InzidenzTodesfall": "float",
                "MeldeTag_Fallsterblichkeit_Prozent": "float",
                "MeldeTag_Vor7Tagen_InzidenzFall": "float",
                "MeldeTag_Vor7Tagen_InzidenzTodesfall": "float",
                "MeldeTag_Vor7Tagen_Fallsterblichkeit_Prozent": "float",
                "InzidenzFall": "float",
                "InzidenzTodesfall": "float",
                "Fallsterblichkeit_Prozent": "float",
                "MeldeTag_InzidenzFall_Gestern": "float",
                "MeldeTag_InzidenzTodesfall_Gestern": "float",
                "MeldeTag_Fallsterblichkeit_Prozent_Gestern": "float",
                "MeldeTag_Vor7Tagen_InzidenzFall_Vor8Tagen": "float",
                "MeldeTag_Vor7Tagen_InzidenzTodesfall_Vor8Tagen": "float",
                "MeldeTag_Vor7Tagen_Fallsterblichkeit_Prozent_Vor8Tagen": "float",
                "MeldeTag_AnzahlFallNeu_7TageSumme": "int",
                "MeldeTag_AnzahlTodesfallNeu_7TageSumme": "int",
                "MeldeTag_Vor7Tagen_AnzahlFallNeu_7TageSumme": "int",
                "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_7TageSumme": "int",
                "AnzahlFallNeu_7TageSumme": "int",
                "AnzahlFallNeu_7TageSumme_Trend": "float",
                "AnzahlFallNeu_7TageSumme_7_Tage_davor": "int",
                "AnzahlTodesfallNeu_7TageSumme": "int",
                "AnzahlTodesfallNeu_7TageSumme_Trend": "float",
                "AnzahlTodesfallNeu_7TageSumme_7_Tage_davor": "int",
                "AnzahlGenesenNeu_7TageSumme": "int",
                "AnzahlGenesenNeu_7TageSumme_Trend": "float",
                "InzidenzFallNeu_7TageSumme": "float",
                "InzidenzFallNeu_7TageSumme_Trend": "float",
                "InzidenzFallNeu_7TageSumme_7_Tage_davor": "float",
                "InzidenzFallNeu_7TageSumme_Trend_Spezial": "float",
                "InzidenzFallNeu_7TageSumme_R": "float",
                "InzidenzFallNeu_Prognose_1_Wochen": "float",
                "InzidenzFallNeu_Prognose_2_Wochen": "float",
                "InzidenzFallNeu_Prognose_4_Wochen": "float",
                "InzidenzFallNeu_Prognose_8_Wochen": "float",
                "InzidenzFallNeu_Tage_bis_50": "float",
                "InzidenzFallNeu_Tage_bis_100": "float",
                "Kontaktrisiko": "float",
                "MeldeTag_AnzahlFallNeu_Gestern_7TageSumme": "int",
                "MeldeTag_AnzahlTodesfallNeu_Gestern_7TageSumme": "int",
                "MeldeTag_Vor7Tagen_AnzahlFallNeu_Vor8Tagen_7TageSumme": "int",
                "MeldeTag_Vor7Tagen_AnzahlTodesfallNeu_Vor8Tagen_7TageSumme": "int",
                "InzidenzTodesfallNeu_7TageSumme": "float",
                "InzidenzTodesfallNeu_7TageSumme_Trend": "float",
                "InzidenzTodesfallNeu_7TageSumme_7_Tage_davor": "float",
                "InzidenzTodesfallNeu_7TageSumme_Trend_Spezial": "float",
                "DatenstandTag_Diff": "int",
                "MeldeTag_InzidenzFallNeu_Gestern_7TageSumme": "float",
                "AnzahlFallNeu_7TageSumme_Dropped": "int",
                "ProzentFallNeu_7TageSumme_Dropped": "float",
                "MeldeTag_Vor7Tagen_InzidenzFallNeu_Vor8Tagen_7TageSumme": "float",
                "MeldeTag_InzidenzFallNeu_Trend": "float",
                "MeldeTag_InzidenzFallNeu_R": "float",
                "MeldeTag_InzidenzFallNeu_Prognose_4_Wochen": "float",
                "PublikationsdauerFallNeu_Min_Neg": "int",
            })

        # data = self._get_data(with_agegroups, data)
        # print(sorted_data)
        data = {}
        # if with_agegroups:
        # data["altersgruppen"] = self._get_agegroups(csv_data)

        data["bundesrepublik"] = self._get_bundesrepublik_data(csv_data)
        self.__process_bundesrepublik(data["bundesrepublik"])
        data["bundeslaender"] = self._get_bundeslaender_data(csv_data)
        self.__process_bundeslaender(data["bundeslaender"])
        data["landkreise"] = self._get_landkreise_data(csv_data)
        self.__process_landkreise(data["landkreise"])
        # f = open("data.json", "w")
        # f.write(json.dumps(data["landkreise"][1001]))
        data = None
        # self._insert_sorted_data(data)
        # self.insert_landkreise_data(full_data)
        # self.insert_faelle_data(full_data)
