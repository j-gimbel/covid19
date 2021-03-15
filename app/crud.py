from sqlalchemy.orm import Session
from . import models, schemas
from sqlalchemy import distinct
from sqlalchemy.sql import func
from datetime import date

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

    # lks = session.query(models.Landkreis).all()
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
            'AnzahlFallNeu-7-Tage-Dropped': row.AnzahlFallNeu_7_Tage_Dropped,
            'AnzahlTodesfallNeu-7-Tage': row.AnzahlTodesfallNeu_7_Tage,
            'Fallsterblichkeit-Prozent': row.Fallsterblichkeit_Prozent,
            'Kontaktrisiko': row.Kontaktrisiko,
            'InzidenzFallNeu-7-Tage': row.InzidenzFallNeu_7_Tage,
            'MeldeDauerFallNeu-Schnitt': row.MeldeDauerFallNeu_Schnitt,
            'InzidenzFallNeu-7-Tage-Trend-Spezial': row.InzidenzFallNeu_7_Tage_Trend_Spezial,
            'Kehrwert_risiko': 1/row.Kontaktrisiko,

        }
        data.append(d)
    return data


def get_covidnumbers(session: Session):

    rows = session.query(models.Bundesrepublik_Daten).with_entities(
        models.Bundesrepublik_Daten.Datum,
        models.Bundesrepublik_Daten.AnzahlFallNeu,
        models.Bundesrepublik_Daten.AnzahlFallNeu_7_Tage,
        models.Bundesrepublik_Daten.AnzahlTodesfallNeu_7_Tage,
        models.Bundesrepublik_Daten.AnzahlFallNeu_7_Tage_Trend,

    ).order_by(models.Bundesrepublik_Daten.Datum).all()

    tests = {

        "11/2020": [128008, 7470, 5.83557277670146, ],
        "12/2020": [374534, 25886, 6.91152205140254, ],
        "13/2020": [377599, 33139, 8.77624146250387, ],
        "14/2020": [417646, 37649, 9.01457214961953, ],
        "15/2020": [386241, 30829, 7.98180410676236, ],
        "16/2020": [339983, 22724, 6.68386360494495, ],
        "17/2020": [363659, 18127, 4.98461470773444, ],
        "18/2020": [327799, 12600, 3.8438189256221, ],
        "19/2020": [385638, 10181, 2.64004065989348, ],
        "20/2020": [431682, 7142, 1.65445860610357, ],
        "21/2020": [356489, 5315, 1.49092959390051, ],
        "22/2020": [408078, 4335, 1.0622969138253, ],
        "23/2020": [342328, 3219, 0.940326236825501, ],
        "24/2020": [327980, 2956, 0.901274467955363, ],
        "25/2020": [384834, 5588, 1.45205465213573, ],
        "26/2020": [472823, 3919, 0.828851388363087, ],
        "27/2020": [512969, 3204, 0.624599147316894, ],
        "28/2020": [513572, 3042, 0.592322011324605, ],
        "29/2020": [544219, 3608, 0.662968400588734, ],
        "30/2020": [556634, 4537, 0.815077771030875, ],
        "31/2020": [589201, 5888, 0.999319417312598, ],
        "32/2020": [719476, 7374, 1.02491257526311, ],
        "33/2020": [871191, 8545, 0.980841170305938, ],
        "34/2020": [1034449, 8868, 0.857267975511601, ],
        "35/2020": [1133623, 8273, 0.729784064014227, ],
        "36/2020": [1052942, 8203, 0.779055256604827, ],
        "37/2020": [1148465, 10403, 0.905817765452147, ],
        "38/2020": [1147879, 13647, 1.1888883758654, ],
        "39/2020": [1220279, 15178, 1.24381391468672, ],
        "40/2020": [1129127, 19930, 1.76508045596288, ],
        "41/2020": [1218988, 30220, 2.47910561875917, ],
        "42/2020": [1284349, 46000, 3.58158101886637, ],
        "43/2020": [1445463, 80097, 5.54126947559363, ],
        "44/2020": [1663992, 118111, 7.09805095216804, ],
        "45/2020": [1634729, 128537, 7.86289348265064, ],
        "46/2020": [1467454, 128986, 8.78978148548438, ],
        "47/2020": [1400145, 131185, 9.36938674208743, ],
        "48/2020": [1381117, 128882, 9.33172207713032, ],
        "49/2020": [1395790, 138305, 9.9087255246133, ],
        "50/2020": [1516038, 169520, 11.181777765465, ],
        "51/2020": [1672033, 188283, 11.2607227249701, ],
        "52/2020": [1090372, 141413, 12.9692435242284, ],
        "53/2020": [845729, 129930, 15.3630772978105, ],
        "1/2021": [1231405, 157772, 12.812356617035, ],
        "2/2021": [1187564, 124037, 10.4446581405297, ],
        "3/2021": [1110190, 110014, 9.90947495473748, ],
        "4/2021": [1148018, 97256, 8.47164417282656, ],
        "5/2021": [1097419, 82288, 7.49832106059764, ],
        "6/2021": [1056768, 67774, 6.41332818556202, ],
        "7/2021": [1098665, 67211, 6.11751534817255, ],
        "8/2021": [1170335, 72008, 6.15276822448273, ],
        "9/2021": [1136825, 70991, 6.24467266289886, ]

    }

    data = [
        ['x'],
        ['Neue Fälle'],
        ["Neue Fälle (7 Tage D.)"],
        ['Neue Todesfälle (7 Tage D.)'],
        ['Wöchentl. Tests'],
        ['7-Tage-R-Wert']
    ]

    for row in rows:

        mydate = date.fromisoformat(row.Datum)
        cw = int(mydate.strftime("%U"))

        y = int(mydate.strftime("%Y"))
        if y == 2020:
            cw = cw+1
        weekday = int(mydate.strftime("%w"))
        if weekday == 0:
            cw = cw - 1
        if cw == 0:
            cw = 53
            y = y-1
        print(str(mydate)+" - "+str(cw)+"/"+str(y))

        data[0].append(row.Datum)

        data[1].append(row.AnzahlFallNeu)
        data[2].append(row.AnzahlFallNeu_7_Tage)
        data[3].append(row.AnzahlTodesfallNeu_7_Tage)
        if str(cw)+"/"+str(y) in tests:
            data[4].append(tests[str(cw) + "/" + str(y)][0])
        else:
            print("not in: "+str(cw)+"/"+str(y))
            data[4].append(None)
        data[5].append(row.AnzahlFallNeu_7_Tage_Trend)

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
