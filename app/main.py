from typing import List
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Covid Risk API Demo ",
    description="Datenquelle: https://pavelmayer.de/covid/risks/ . This is a private site in test mode, data validitiy cannot be guaranteed. Hinweis: Dies ist eine privat betriebene Seite im Testbetrieb, für die Richtigkeit der Berechnung und der Ergebnisse gibt es keine Gewähr.",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get(
    "/api/bundeslaender",  # ,
    response_model=List[schemas.Bundesland_Base],
)
async def bundeslaender_daten(session: Session = Depends(get_db)):
    return crud.get_bundeslaender_daten(session=session)

@app.get(
    "/api/bundesland/{kuerzel}",  # ,
    response_model=List[schemas.Bundesland_Data_Base],
)
async def bundesland_daten(kuerzel: str, session: Session = Depends(get_db)):
    return crud.get_bundesland_daten(session=session, kuerzel=kuerzel)

@app.get(
    "/api/map/demo",  # ,
    response_model=List[schemas.GeoDemo_Base],
)
async def geojson_demo(date: str, session: Session = Depends(get_db)):
    return crud.get_geojson_demo(session=session, date=date)
