from sqlalchemy.orm import Session
from . import models, schemas
from sqlalchemy import distinct
from sqlalchemy.sql import func


def get_bundeslaender_daten(session: Session):
    """
    result = (
        session.query(models.Bundesland_Daten_Taeglich)
        .join(models.Bundesland_Daten_Taeglich.bundesland_id)
        .distinct()
        .order_by(models.Bundesland_Daten_Taeglich.Aktualisierung)
        .all()
    )"""

    return session.query(models.Bundesland).all()


def get_bundesland_daten(session: Session, kuerzel: str):
    """
    result = (
        session.query(models.Bundesland_Daten_Taeglich)
        .join(models.Bundesland_Daten_Taeglich.bundesland_id)
        .distinct()
        .order_by(models.Bundesland_Daten_Taeglich.Aktualisierung)
        .all()
    )"""
    sa_bundesland = session.query(models.Bundesland).filter_by(Kuerzel=kuerzel.upper()).one()
    rows = session.query(models.Bundesland_Daten).filter_by(Bundesland_ID=sa_bundesland.ID).all()
    return rows

def get_geojson_demo(session: Session, date: str):

    #lks = session.query(models.Landkreis).all()
    lk_data = session.query(models.Landkreis_Daten).filter_by(Datum=date).join(models.Landkreis_Daten.Landkreis).with_entities(
        models.Landkreis,
        models.Landkreis_Daten.AnzahlFallNeu,
        models.Landkreis_Daten.AnzahlFallNeu_7_Tage_Dropped,
        models.Landkreis_Daten.AnzahlTodesfallNeu_7_Tage,
        models.Landkreis_Daten.Fallsterblichkeit_Prozent,
        models.Landkreis_Daten.Kontaktrisiko,
        models.Landkreis_Daten.InzidenzFallNeu_7_Tage,
        models.Landkreis_Daten.MeldeDauerFallNeu_Schnitt,
        models.Landkreis_Daten.InzidenzFallNeu_7_Tage_Trend_Spezial,

    ).all()

    data = []
    for row in lk_data:
        print(row)
        d = {
            'Landkreis': row.Landkreis.Name,
            'Bundesland': row.Landkreis.Bundesland.Name,
            'Einwohner': row.Landkreis.Einwohner,
            'AnzahlFallNeu': row.AnzahlFallNeu,
            'AnzahlFallNeu_7_Tage_Dropped': row.AnzahlFallNeu_7_Tage_Dropped,
            'AnzahlTodesfallNeu_7_Tage': row.AnzahlTodesfallNeu_7_Tage,
            'Fallsterblichkeit_Prozent': row.Fallsterblichkeit_Prozent,
            'Kontaktrisiko': row.Kontaktrisiko,
            'InzidenzFallNeu_7_Tage': row.InzidenzFallNeu_7_Tage,
            'MeldeDauerFallNeu_Schnitt': row.MeldeDauerFallNeu_Schnitt,
            'InzidenzFallNeu_7_Tage_Trend_Spezial': row.InzidenzFallNeu_7_Tage_Trend_Spezial,
            'Kehrwert_risiko': 1/row.Kontaktrisiko,

        }
        data.append(d)
    return data


"""

'Landkreis': row.Landkreis.Name
'Bundesland': row.Landkreis.Bundesland.Name,
'Einwohner': row.Landkreis.Einwohner,
'AnzahlFallNeu': row.AnzahlFallNeu,
'AnzahlFallNeu_7_Tage_Dropped': row.AnzahlFallNeu_7_Tage_Dropped,
'AnzahlTodesfallNeu_7_Tage': row.AnzahlTodesfallNeu_7_Tage,
'Fallsterblichkeit_Prozent': row.Fallsterblichkeit_Prozent,
'Kontaktrisiko': row.Kontaktrisiko,
'InzidenzFallNeu_7_Tage': row.InzidenzFallNeu_7_Tage,
'MeldeDauerFallNeu_Schnitt': row.MeldeDauerFallNeu_Schnitt,
'InzidenzFallNeu_7_Tage_Trend_Spezial': row.InzidenzFallNeu_7_Tage_Trend_Spezial,
'Kehrwert_risiko': 1/row.Kontaktrisiko,
"""
