from sqlalchemy.orm import Session
from . import models, schemas
from sqlalchemy import distinct
from sqlalchemy.sql import func


def get_data_for_bundeslaender(session: Session, date: str):

    """
    result = (
        session.query(models.Bundesland_Daten_Taeglich)
        .join(models.Bundesland_Daten_Taeglich.bundesland_id)
        .distinct()
        .order_by(models.Bundesland_Daten_Taeglich.Aktualisierung)
        .all()
    )"""

    bundesland_data = (
        session.query(models.Bundesland_Daten_Taeglich)
        .order_by(models.Bundesland_Daten_Taeglich.Aktualisierung)
        .first()
    )

    newest_date = bundesland_data.Aktualisierung

    # return date

    data = (
        session.query(models.Bundesland_Daten_Taeglich)
        .filter_by(Aktualisierung=newest_date)
        .all()
    )
    return data
