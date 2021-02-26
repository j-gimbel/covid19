import sqlite3
import json
from sqlalchemy.orm import Session
import logging
import requests
import os.path as path
import csv
from datetime import date, datetime

from app import models  # ,crud,  schemas
from app.database import SessionLocal, engine

"""
Bsp. Verknüfung der Daten anhand einer ID
Schelswig Holsten / Flensburg:

Bundesländer OBJECTID_1 = 1 /   OBJECTID = 15 dies ist unwichtig
Landkreise: BL_ID = 1
Cov19 Fall : IdBundesland = 1
"""

if __name__ == "__main__":

    date_today = date.today().isoformat()

    # create logger
    logger = logging.getLogger("populate_db")
    logger.setLevel(logging.DEBUG)

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
    logger.addHandler(ch)

    # create file handler and set level to debug
    fh = logging.FileHandler("populate_db.log")
    fh.setLevel(logging.DEBUG)
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(fh)

    logger.info("clearing DB")
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    filepath = "downloads/" + date_today + "_RKI_Corona_Bundeslaender.csv"
    logger.info("reading " + filepath)
    rows = []

    with open(filepath, "r", encoding="utf-8-sig") as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            rows.append(row)

    header = rows[0]
    if (
        header
        != "OBJECTID_1,LAN_ew_AGS,LAN_ew_GEN,LAN_ew_BEZ,LAN_ew_EWZ,OBJECTID,Fallzahl,Aktualisierung,AGS_TXT,GlobalID,faelle_100000_EW,Death,cases7_bl_per_100k,cases7_bl,death7_bl,cases7_bl_per_100k_txt,AdmUnitId,SHAPE_Length,SHAPE_Area".split(
            ","
        )
    ):
        raise Exception("Bad Header " + filepath)
    for i in range(1, len(rows)):
        row = rows[i]
        if len(row) < 10:
            continue
        bundesland = models.Bundesland(
            ID=row[header.index("OBJECTID_1")],
            LAN_ew_GEN=row[header.index("LAN_ew_GEN")],
            LAN_ew_BEZ=row[header.index("LAN_ew_BEZ")],
            LAN_ew_EWZ=row[header.index("LAN_ew_EWZ")],
        )

        db.query(models.Bundesland_Daten_Taeglich).filter_by()

        aktualisierung_datetime = datetime.strptime(
            row[header.index("Aktualisierung")], "%Y/%m/%d %H:%M:%S+00"
        )
        aktualisierung_timestamp = int(datetime.timestamp(aktualisierung_datetime))

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
            db.add(bundesland)
            bundesland.taegliche_daten.append(bundesland_daten_taeglich)
        except Exception as e:
            logger.error(
                "Error :"
                + str(e)
                + " while trying to process line "
                + line
                + "with data "
                + json.dumps(e)
            )

    db.commit()

    bundeslaender = db.query(models.Bundesland).distinct(models.Bundesland.ID).all()
    bundeslaender_per_ID = {}
    for b in bundeslaender:
        bundeslaender_per_ID[b.ID] = b

    filepath = "downloads/" + date_today + "_RKI_Corona_Landkreise.csv"
    logger.info("reading " + filepath)
    rows = []
    with open(filepath, "r", encoding="utf-8-sig") as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            rows.append(row)

    header = rows[0]
    if (
        header
        != "OBJECTID,ADE,GF,BSG,RS,AGS,SDV_RS,GEN,BEZ,IBZ,BEM,NBD,SN_L,SN_R,SN_K,SN_V1,SN_V2,SN_G,FK_S3,NUTS,RS_0,AGS_0,WSK,EWZ,KFL,DEBKG_ID,death_rate,cases,deaths,cases_per_100k,cases_per_population,BL,BL_ID,county,last_update,cases7_per_100k,recovered,EWZ_BL,cases7_bl_per_100k,cases7_bl,death7_bl,cases7_lk,death7_lk,cases7_per_100k_txt,AdmUnitId,SHAPE_Length,SHAPE_Area".split(
            ","
        )
    ):
        raise Exception("Bad Header in rki/RKI_Corona_Landkreise.csv")

    for i in range(1, len(rows)):
        # while True:
        """
        line = f.readline().rstrip()
        if line == "" or line == None:
            break
        d = line.split(",")
        """

        last_update_datetime = datetime.strptime(
            row[header.index("last_update")], "%d.%m.%Y, %H:%M Uhr"
        )
        last_update_timestamp = int(datetime.timestamp(last_update_datetime))

        row = rows[i]
        landkreis = models.Landkreis(
            ID=row[header.index("OBJECTID")],
            RS=row[header.index("RS")],
            AGS=row[header.index("AGS")],
            GEN=row[header.index("GEN")],
            BEZ=row[header.index("BEZ")],
            EWZ=row[header.index("EWZ")],
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
        )
        bl_ID = row[header.index("BL_ID")]
        landkreis.bundesland = bundeslaender_per_ID[int(bl_ID)]

        # bundeslaender_per_Irow[int(bl_ID)].landkreis.append(landkreis)

    db.commit()

    filepath = "downloads/RKI_COVID19.csv"
    logger.info("reading " + filepath)
    rows = []

    with open(filepath, "r", encoding="utf-8-sig") as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            rows.append(row)

    header = rows[0]
    if (
        header
        != "ObjectId,IdBundesland,Bundesland,Landkreis,Altersgruppe,Geschlecht,AnzahlFall,AnzahlTodesfall,Meldedatum,IdLandkreis,Datenstand,NeuerFall,NeuerTodesfall,Refdatum,NeuGenesen,AnzahlGenesen,IstErkrankungsbeginn,Altersgruppe2".split(
            ","
        )
    ):
        raise Exception("Bad Header in " + filepath)

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
        print(ag_name)
        altersgruppe = models.Altersgruppe(name=ag_name)
        db.add(altersgruppe)
        altersgruppe_per_name[ag_name] = altersgruppe
    db.commit()

    # alle Landkreise laden

    landkreise = db.query(models.Landkreis).all()
    landkreise_per_AGS_ID = {}
    for lk in landkreise:
        landkreise_per_AGS_ID[lk.AGS] = lk

    # alle Bundesländer  laden
    bundeslaender = db.query(models.Bundesland).all()
    bundeslaender_per_ID = {}
    for bl in bundeslaender:
        bundeslaender_per_ID[bl.ID] = bl

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
        if len(row) < 10:
            continue

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

        fall = models.Fall(
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
        fall.altersgruppe = altersgruppe_per_name[altersgruppe_string]
        fall.landkreis = landkreise_per_AGS_ID[int(ID_Landkreis)]

        fall.bundesland = bundeslaender_per_ID[int(ID_Bundesland)]

        db.add(fall)

        if counter > 10000:

            percent = round((i + 1) / len(rows) * 100, 1)
            logger.info(str(percent) + "% done")
            db.commit()
            counter = 0
    db.commit()
