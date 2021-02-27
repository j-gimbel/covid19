from .db import DB

if __name__ == "__main__":

    # query = db.query(func.max(models.Bundesland_Daten_Taeglich.Aktualisierung))

    # letzte_Aktualisierung = query.first()
    print(letzte_Aktualisierung[0])
    db.update()