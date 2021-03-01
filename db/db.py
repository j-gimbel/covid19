import sqlite3
import json
from sqlalchemy.orm import Session
import logging
import requests
import os
import csv
import shutil
import gzip
from datetime import date, datetime, timedelta

from app import models  # ,crud,  schemas
from app.database import SessionLocal, engine


import hashlib


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def read_data_from_csv(filepath: str, expected_header_line: str):

    if not os.path.isfile(filepath):
        raise Exception("File " + filepath + " not found")
    rows = []

    # with open(filepath, "r", encoding="utf-8-sig") as csvfile:
    csv_list = []
    with gzip.open(filepath, "rb") as f:

        tmp_file = open("temp.tmp", "wb")
        tmp_file.write(f.read())
        tmp_file.close()

        with open("temp.tmp", "r", encoding="utf-8-sig") as csvfile:

            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                rows.append(row)
    if rows[0] != expected_header_line.split(","):
        raise Exception("Bad Header " + filepath)
    return rows


class DB:

    session = None

    def __init__(self):

        models.Base.metadata.create_all(bind=engine)
        self.session = SessionLocal()
        self.date_today = date.today().isoformat()

        self.sources = json.load(
            open(os.path.dirname(__file__) + "/../rki/sources.json", "r")
        )

        self.data_dir = "downloads"

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
        self.logger.info("clearing DB")

    """

    def bundeslaender_data_update_from_csv(self):

        # bundeslaender = self.session.query(models.Bundesland).all()

        bundesland_data = (
            self.session.query(models.Bundesland_Daten_Taeglich)
            .order_by(models.Bundesland_Daten_Taeglich.Aktualisierung.desc())
            .first()
        )

        last_aktualisierung_timestamp = int(bundesland_data.Aktualisierung)
        last_aktualisierung_date = datetime.fromtimestamp(last_aktualisierung_timestamp)
        next_day = last_aktualisierung_date + timedelta(days=1)
        while True:
            date = next_day.date().isoformat()
            file = self.data_dir + "/" + date + "_RKI_Corona_Bundeslaender.csv.gz"
            if os.path.isfile(file):
                self.insert_bundeslaender_data_from_csv(date)
            else:
                self.logger.info("file does not exist " + file + ". stopping update")
                break
            next_day += timedelta(days=1)
    """

    def insert_bundeslaender_data_from_csv(self, date: str, filepath: str):

        # filepath = self.data_dir + "/" + date + "_RKI_Corona_Bundeslaender.csv.gz"

        if not os.path.isfile(filepath):
            self.logger.warning("Cound not find file " + filepath)
            return
        self.logger.info("reading " + filepath)
        rows = []

        rows = read_data_from_csv(
            filepath=filepath,
            expected_header_line="OBJECTID_1,LAN_ew_AGS,LAN_ew_GEN,LAN_ew_BEZ,LAN_ew_EWZ,OBJECTID,Fallzahl,Aktualisierung,AGS_TXT,GlobalID,faelle_100000_EW,Death,cases7_bl_per_100k,cases7_bl,death7_bl,cases7_bl_per_100k_txt,AdmUnitId,SHAPE_Length,SHAPE_Area",
        )

        header = rows[0]
        for i in range(1, len(rows)):
            row = rows[i]

            # if len(row) < 10:
            #    continue

            bundesland_ID = row[header.index("OBJECTID_1")]

            # get bundesland from db or create it
            bundesland = (
                self.session.query(models.Bundesland)
                .filter_by(ID=bundesland_ID)
                .one_or_none()
            )

            if bundesland is None:
                bundesland = models.Bundesland(
                    ID=bundesland_ID,
                    LAN_ew_GEN=row[header.index("LAN_ew_GEN")],
                    LAN_ew_BEZ=row[header.index("LAN_ew_BEZ")],
                    LAN_ew_EWZ=row[header.index("LAN_ew_EWZ")],
                )
                self.session.add(bundesland)

            aktualisierung_datetime = datetime.strptime(
                row[header.index("Aktualisierung")], "%Y/%m/%d %H:%M:%S+00"
            )
            aktualisierung_timestamp = int(datetime.timestamp(aktualisierung_datetime))

            # check if current data is already in db by checking the timestamp
            bundesland_daten_taeglich = (
                self.session.query(models.Bundesland_Daten_Taeglich)
                .filter(
                    (models.Bundesland_Daten_Taeglich.bundesland_id == bundesland_ID),
                    (
                        models.Bundesland_Daten_Taeglich.Aktualisierung
                        == aktualisierung_timestamp
                    ),
                )
                .one_or_none()
            )

            if bundesland_daten_taeglich is None:
                self.logger.info("Addingd data for " + bundesland.LAN_ew_GEN)
                bundesland_daten_taeglich = models.Bundesland_Daten_Taeglich(
                    Fallzahl=row[header.index("Fallzahl")],
                    Aktualisierung=aktualisierung_timestamp,
                    faelle_100000_EW=row[header.index("faelle_100000_EW")],
                    Death=row[header.index("Death")],
                    cases7_bl_per_100k=row[header.index("cases7_bl_per_100k")],
                    cases7_bl=row[header.index("cases7_bl")],
                    death7_bl=row[header.index("death7_bl")],
                )

                try:

                    bundesland.taegliche_daten.append(bundesland_daten_taeglich)
                except Exception as e:
                    print(e)
                    print(row)
                    self.logger.error(
                        "Error :"
                        + str(e)
                        + " while trying to process line "
                        + row
                        + "with data "
                        + json.dumps(e)
                    )
            else:
                self.logger.warning(
                    "Data for "
                    + bundesland.LAN_ew_GEN
                    + " for date "
                    + date
                    + " already in db"
                )
        Inserted_csv_File = models.Inserted_csv_File(
            data_type="Bundesland",
            date=date,
            md5sum=md5(filepath),
            file_path=filepath,
            date_file_processed=datetime.now().isoformat(),
        )
        self.session.add(Inserted_csv_File)
        self.session.commit()

    """
    def landkreise_data_update_from_csv(filepath:str):

        landkreise_data = (
            self.session.query(models.Landkreis_Daten_Taeglich)
            .order_by(models.Landkreis_Daten_Taeglich.last_update.desc())
            .first()
        )

        last_update_timestamp = int(landkreise_data.last_update)
        last_update_date = datetime.fromtimestamp(last_update_timestamp)
        next_day = last_update_date + timedelta(days=1)
        while True:
            date = next_day.date().isoformat()
            file = self.data_dir + "/" + date + "_RKI_Corona_Landkreise.csv.gz"
            if os.path.isfile(file):
                self.insert_landkreise_data_from_csv(date)
            else:
                self.logger.info("file does not exist " + file + ". stopping update")
                break
            next_day += timedelta(days=1)
    """

    def insert_landkreise_data_from_csv(self, date: str, filepath: str):

        # filepath = self.data_dir + "/" + date + "_RKI_Corona_Landkreise.csv.gz"
        if not os.path.isfile(filepath):
            self.logger.warning("Cound not find file " + filepath)
            return
        self.logger.info("reading " + filepath)
        rows = []

        rows = read_data_from_csv(
            filepath=filepath,
            expected_header_line="OBJECTID,ADE,GF,BSG,RS,AGS,SDV_RS,GEN,BEZ,IBZ,BEM,NBD,SN_L,SN_R,SN_K,SN_V1,SN_V2,SN_G,FK_S3,NUTS,RS_0,AGS_0,WSK,EWZ,KFL,DEBKG_ID,death_rate,cases,deaths,cases_per_100k,cases_per_population,BL,BL_ID,county,last_update,cases7_per_100k,recovered,EWZ_BL,cases7_bl_per_100k,cases7_bl,death7_bl,cases7_lk,death7_lk,cases7_per_100k_txt,AdmUnitId,SHAPE_Length,SHAPE_Area",
        )

        header = rows[0]
        for i in range(1, len(rows)):
            row = rows[i]
            landkreis_ID = row[header.index("OBJECTID")]

            # get landkreis from db or create it
            landkreis = (
                self.session.query(models.Landkreis)
                .filter_by(ID=landkreis_ID)
                .one_or_none()
            )

            if landkreis is None:
                landkreis = models.Landkreis(
                    ID=landkreis_ID,
                    RS=row[header.index("RS")],
                    AGS=row[header.index("AGS")],
                    GEN=row[header.index("GEN")],
                    BEZ=row[header.index("BEZ")],
                    EWZ=row[header.index("EWZ")],
                    BL_ID=row[header.index("BL_ID")],
                )
                self.session.add(landkreis)
            # else:
            #    print("TODO: update it if necessary !")
            # check if current data is already in db by checking the timestamp

            last_update_datetime = datetime.strptime(
                row[header.index("last_update")], "%d.%m.%Y, %H:%M Uhr"
            )
            last_update_timestamp = int(datetime.timestamp(last_update_datetime))

            # check if current data is already in db by checking the timestamp
            landkreis_daten_taeglich = (
                self.session.query(models.Landkreis_Daten_Taeglich)
                .filter(
                    (models.Landkreis_Daten_Taeglich.landkreis_id == landkreis_ID),
                    (
                        models.Landkreis_Daten_Taeglich.last_update
                        == last_update_timestamp
                    ),
                )
                .one_or_none()
            )

            if landkreis_daten_taeglich is None:
                self.logger.info("Adding data for " + landkreis.GEN)
                landkreis_daten_taeglich = models.Landkreis_Daten_Taeglich(
                    death_rate=row[header.index("death_rate")],
                    cases=row[header.index("cases")],
                    deaths=row[header.index("deaths")],
                    cases_per_100k=row[header.index("cases_per_100k")],
                    cases_per_population=row[header.index("cases_per_population")],
                    county=row[header.index("county")],
                    last_update=last_update_timestamp,
                    cases7_per_100k=row[header.index("cases7_per_100k")],
                    cases7_lk=row[header.index("cases7_lk")],
                    death7_lk=row[header.index("death7_lk")],
                    landkreis_id=landkreis_ID,
                )

                try:

                    self.session.add(landkreis_daten_taeglich)
                except Exception as e:
                    print(e)
                    print(row)
                    self.logger.error(
                        "Error :"
                        + str(e)
                        + " while trying to process line "
                        + row
                        + "with data "
                        + json.dumps(e)
                    )
            else:
                self.logger.warning(
                    "Data for " + landkreis.GEN + " for date " + date + " already in db"
                )

        Inserted_csv_File = models.Inserted_csv_File(
            data_type="Landkreis",
            date=date,
            md5sum=md5(filepath),
            file_path=filepath,
            date_file_processed=datetime.now().isoformat(),
        )
        self.session.add(Inserted_csv_File)
        self.session.commit()

    def insert_or_update_faelle_data_from_csv(self, date: str, filepath: str):

        """
        Achtung: diese funktion nur auf leere Tabellen für Altersgruppen, Faelle anwenden !
        """

        # filepath = self.data_dir + "/" + date + "_RKI_COVID19.csv.gz"
        if not os.path.isfile(filepath):
            self.logger.warning("Cound not find file " + filepath)
            return
        rows = []

        rows = read_data_from_csv(
            filepath=filepath,
            expected_header_line="ObjectId,IdBundesland,Bundesland,Landkreis,Altersgruppe,Geschlecht,AnzahlFall,AnzahlTodesfall,Meldedatum,IdLandkreis,Datenstand,NeuerFall,NeuerTodesfall,Refdatum,NeuGenesen,AnzahlGenesen,IstErkrankungsbeginn,Altersgruppe2",
        )

        header = rows[0]

        # Alle einzigartigen Altersgruppen finden
        altersgruppen_set = set()
        ag_index = header.index("Altersgruppe")
        for i in range(1, len(rows)):
            row = rows[i]
            altersgruppe_string = row[ag_index]
            altersgruppen_set.add(altersgruppe_string)

        # alle Altersgruppen einfügen
        altersgruppe_per_name = {}
        for ag_name in altersgruppen_set:
            altersgruppe = models.Altersgruppe(name=ag_name)
            self.session.add(altersgruppe)
            altersgruppe_per_name[ag_name] = altersgruppe
        self.session.commit()

        # alle Landkreise laden

        landkreise = self.session.query(models.Landkreis).all()
        landkreise_per_RS_ID = {}
        for lk in landkreise:
            landkreise_per_RS_ID[int(lk.RS)] = lk

        # alle Bundesländer  laden
        bundeslaender = self.session.query(models.Bundesland).all()
        bundeslaender_per_ID = {}
        for bl in bundeslaender:
            bundeslaender_per_ID[bl.ID] = bl

        objectId_index = header.index("ObjectId")
        IdBundesland = header.index("IdBundesland")

        altersgruppe_index = header.index("Altersgruppe")
        geschlecht_index = header.index("Geschlecht")
        anzahlFall_index = header.index("AnzahlFall")
        anzahlTodesFall_index = header.index("AnzahlTodesfall")
        meldeDatum_index = header.index("Meldedatum")
        idLandkreis_index = header.index("IdLandkreis")
        datenStand_index = header.index("Datenstand")
        neuerFall_index = header.index("NeuerFall")
        neuerTodesFall_index = header.index("NeuerTodesfall")
        refDatum_index = header.index("Refdatum")
        neuGenesen_index = header.index("NeuGenesen")
        anzahlGenesen_index = header.index("AnzahlGenesen")
        istErkrankungsbeginn_index = header.index("IstErkrankungsbeginn")
        altersgruppe2_index = header.index("Altersgruppe2")

        counter = 0

        for i in range(1, len(rows)):
            counter += 1
            row = rows[i]

            ID = row[objectId_index]

            altersgruppe_string = row[altersgruppe_index]

            meldeDatum_datetime = datetime.strptime(
                row[header.index("Meldedatum")], "%Y/%m/%d %H:%M:%S+00"
            )
            meldeDatum_timestamp = int(datetime.timestamp(meldeDatum_datetime))

            datenStand_datetime = datetime.strptime(
                row[header.index("Datenstand")], "%d.%m.%Y, %H:%M Uhr"
            )
            datenStand_timestamp = int(datetime.timestamp(datenStand_datetime))

            refDatum_datetime = datetime.strptime(
                row[header.index("Refdatum")], "%Y/%m/%d %H:%M:%S+00"
            )
            refDatum_timestamp = int(datetime.timestamp(refDatum_datetime))

            ID_Landkreis = row[idLandkreis_index]
            ID_Bundesland = row[IdBundesland]

            fall_daten_taeglich = (
                self.session.query(models.Fall_Daten_Taeglich)
                .filter_by(ID=ID)
                .one_or_none()
            )

            if fall_daten_taeglich is None:
                fall_daten_taeglich = models.Fall_Daten_Taeglich(
                    geschlecht=row[geschlecht_index],
                    anzahlFall=row[anzahlFall_index],
                    anzahlTodesFall=row[anzahlTodesFall_index],
                    meldeDatum=meldeDatum_datetime,
                    datenStand=datenStand_timestamp,
                    neuerFall=row[neuerFall_index],
                    neuerTodesFall=row[neuerTodesFall_index],
                    refDatum=refDatum_timestamp,
                    neuGenesen=row[neuGenesen_index],
                    anzahlGenesen=row[anzahlGenesen_index],
                    istErkrankungsbeginn=bool(int(row[istErkrankungsbeginn_index])),
                    altersgruppe2=row[altersgruppe2_index],
                )
                fall_daten_taeglich.altersgruppe = altersgruppe_per_name[
                    altersgruppe_string
                ]

                fall_daten_taeglich.landkreis = landkreise_per_RS_ID[int(ID_Landkreis)]
                fall_daten_taeglich.bundesland = bundeslaender_per_ID[
                    int(ID_Bundesland)
                ]
                self.session.add(fall_daten_taeglich)
            else:

                data_to_update = {}
                data_to_update["geschlecht"] = row[geschlecht_index]
                data_to_update["anzahlFall"] = row[anzahlFall_index]
                data_to_update["anzahlTodesFall"] = row[anzahlTodesFall_index]
                data_to_update["meldeDatum"] = meldeDatum_datetime
                data_to_update["neuerFall"] = row[neuerFall_index]
                data_to_update["neuerTodesFall"] = row[neuerTodesFall_index]
                data_to_update["refDatum"] = refDatum_timestamp
                data_to_update["neuGenesen"] = row[neuGenesen_index]
                data_to_update["anzahlGenesen"] = row[anzahlGenesen_index]
                data_to_update["istErkrankungsbeginn"] = bool(
                    int(row[istErkrankungsbeginn_index])
                )
                data_to_update["altersgruppe2"] = row[altersgruppe2_index]

                for (key, value) in data_to_update:

                    if value != getattr(fall_daten_taeglich, key):
                        self.logger.info(
                            "updated value for key "
                            + key
                            + "="
                            + str(value)
                            + " in row "
                            + str(i + 1)
                        )

                fall_daten_taeglich

            if counter > 10000:

                percent = round((i + 1) / len(rows) * 100, 1)
                self.logger.info("adding Faelle, " + str(percent) + "% done")
                self.session.commit()
                counter = 0
        Inserted_csv_File = models.Inserted_csv_File(
            data_type="Fall",
            date=date,
            md5sum=md5(filepath),
            file_path=filepath,
            date_file_processed=datetime.now().isoformat(),
        )
        self.session.add(Inserted_csv_File)
        self.session.commit()

    def _clear_db(self):
        print("clearing")
        self.session.close()
        print(os.path.dirname(__file__) + "/../database.db")
        os.remove(os.path.dirname(__file__) + "/../database.db")
        # print(models.Base.metadata.tables.values())
        # models.Base.metadata.drop_all(bind=engine)
        models.Base.metadata.create_all(bind=engine)
        self.session = SessionLocal()

    def create(self, date):

        from sqlalchemy.engine import Engine
        from sqlalchemy import event

        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            # print("event")
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=OFF")
            cursor.execute("PRAGMA cache_size = 100000")
            cursor.execute("PRAGMA SYNCHRONOUS = OFF")
            cursor.execute("PRAGMA LOCKING_MODE = EXCLUSIVE")
            cursor.close()

        self._clear_db()
        self.insert_bundeslaender_data_from_csv(
            date=date,
            filepath=self.data_dir + "/" + date + "_RKI_Corona_Bundeslaender.csv.gz",
        )
        self.insert_landkreise_data_from_csv(
            date=date,
            filepath=self.data_dir + "/" + date + "_RKI_Corona_Landkreise.csv.gz",
        )
        self.insert_or_update_faelle_data_from_csv(
            date=date, filepath=self.data_dir + "/" + date + "_RKI_COVID19.csv.gz"
        )

        self.update()

    # get last date of data from table

    def update(self):

        self.bundeslaender_data_update_from_csv()
        self.landkreise_data_update_from_csv()
        self.faelle_data_update_from_csv()
