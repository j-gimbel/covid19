from typing import List, Optional

from pydantic import BaseModel


class Bundesland_Base(BaseModel):
    Name: str
    Kuerzel: str
    Einwohner: int
    Flaeche: float
    Dichte: float

    class Config:
        orm_mode = True


class Bundesland_Data_Base(BaseModel):
    Datum: str
    AnzahlFall: str
    AnzahlTodesfall: str
    AnzahlGenesen: str
    Kontaktrisiko: Optional[float]

    class Config:
        orm_mode = True


class GeoDemo_Base(BaseModel):

    AnzahlFallNeu: int

    Landkreis: str
    Einwohner: int
    Bundesland: str

    AnzahlFallNeu_7_Tage_Dropped: int
    AnzahlTodesfallNeu_7_Tage: int
    Fallsterblichkeit_Prozent: float
    Kontaktrisiko: float
    InzidenzFallNeu_7_Tage: float
    MeldeDauerFallNeu_Schnitt: float
    InzidenzFallNeu_7_Tage_Trend_Spezial: float
    Kehrwert_risiko: float

    class Config:
        orm_mode = True
