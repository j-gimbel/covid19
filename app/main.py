from typing import List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Covid 19 API Demo",
    description="Datenquelle: RKI COVID-19 Datenhub, https://npgeo-corona-npgeo-de.hub.arcgis.com/search?collection=Dataset/",
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get(
    "/api/bundeslaender/latest",  # ,
    response_model=List[schemas.Bundesland_Daten_Taeglich_Mit_Bundesland],
)
def bundeslaender_letzte_daten(session: Session = Depends(get_db)):
    return crud.get_data_for_bundeslaender(session=session, date="latest")
