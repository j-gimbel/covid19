import sqlite3
import json
from sqlalchemy.orm import Session
from app import models  # ,crud,  schemas
from app.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

"""
Bsp. Verknüfung der Daten anhand einer ID
Schelswig Holsten / Flensburg:

Bundesländer OBJECTID_1 = 1 /   OBJECTID = 15 dies ist unwichtig
Landkreise: BL_ID = 1
Cov19 Fall : IdBundesland = 1
"""

if __name__ == "__main__":

    f = open("rki/RKI_Corona_Bundeslaender.csv", "r", encoding="utf-8-sig")
    line = f.readline().rstrip()

    headers = line.split(",")
    if (
        headers
        != "OBJECTID_1,LAN_ew_AGS,LAN_ew_GEN,LAN_ew_BEZ,LAN_ew_EWZ,OBJECTID,Fallzahl,Aktualisierung,AGS_TXT,GlobalID,faelle_100000_EW,Death,cases7_bl_per_100k,cases7_bl,death7_bl,cases7_bl_per_100k_txt,AdmUnitId,SHAPE_Length,SHAPE_Area".split(
            ","
        )
    ):
        print(headers)
        print(
            "OBJECTID_1,LAN_ew_AGS,LAN_ew_GEN,LAN_ew_BEZ,LAN_ew_EWZ,OBJECTID,Fallzahl,Aktualisierung,AGS_TXT,GlobalID,faelle_100000_EW,Death,cases7_bl_per_100k,cases7_bl,death7_bl,cases7_bl_per_100k_txt,AdmUnitId,SHAPE_Length,SHAPE_Area".split(
                ","
            )
        )
        raise Exception("Bad Header in rki/RKI_Corona_Bundeslaender.csv")

    """
    0 OBJECTID_1 "id":  -> FK von RKI_COVID19 (IdBundesland) und Landkreise (BL_ID)
    1 LAN_ew_AGS  # lfd nummer zweistellig 
    2 LAN_ew_GEN - "name"
    3 LAN_ew_BEZ - "typ": Bezeichnung Land/Hansestadt...
    4 LAN_ew_EWZ - "einwohnerzahl": Einwohnerzahl
    5 OBJECTID - FK von RKI Corona Landkreise (Bundesland ID )
    6 Fallzahl - "fallzahl": Anzahl Fälle
    7 Aktualisierung - datum d. Aktualisierung
    8 AGS_TXT - irgend eine # lfd nummer zweistellig
    9 GlobalID 
    10 faelle_100000_EW - fälle pro 100000 EW
    11 Death - tote gesamt
    12 cases7_bl_per_100k - 7 tages mittelwert fälle/100000 EW
    13 cases7_bl - 7 tages mittelwert fälle
    14 death7_bl - 7 tages mittelwert tote
    15 cases7_bl_per_100k_txt
    16 AdmUnitId - noch ne ID
    17 SHAPE_Length - irgend deine Längenangabe
    18 SHAPE_Area - irgend deine Längenangabe
    """

    while True:
        line = f.readline()
        if line == "" or line == None:
            break

        d = line.split(",")

        bundesland = models.Bundesland(
            OBJECTID_1=int(d[0]),
            LAN_ew_GEN=str(d[2]),
            LAN_ew_BEZ=str(d[3]),
            LAN_ew_EWZ=int(d[4]),
            Fallzahl=int(d[6]),
            Aktualisierung=str(d[7]),
            faelle_100000_EW=float(d[10]),
            Death=int(d[11]),
            cases7_bl_per_100k=float(d[12]),
            cases7_bl=float(d[13]),
            death7_bl=float(d[14]),
        )
        db.add(bundesland)

    db.commit()

    f = open("rki/RKI_COVID19.csv", "r")
    line = f.readline()
    headers = line.split(",")

    while True:
        line = f.readline()
        if line == "" or line == None:
            break

        d = line.split(",")
