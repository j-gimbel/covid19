from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field


class Bundesland_Base(BaseModel):
    ID: int
    Name: str
    Kuerzel: str
    Einwohner: int
    Flaeche: float
    Einwohner: int
    Einwohner_AG_A00_A04: int
    Einwohner_AG_A05_A14: int
    Einwohner_AG_A15_A34: int
    Einwohner_AG_A35_A59: int
    Einwohner_AG_A60_A79: int
    Einwohner_AG_A80Plus: int

    class Config:
        orm_mode = True


"""
class Bundesland_Data_Base(BaseModel):
    Datum: date
    AnzahlFall: str
    AnzahlTodesfall: str
    AnzahlGenesen: str
    Kontaktrisiko: Optional[float]

    class Config:
        orm_mode = True
"""

class Landkreise_Base(BaseModel):
    ID: int
    Name: str
    Typ: str
    # Einwohner: int
    # Flaeche: float

    class Config:
        orm_mode = True


class Lankreis_Data_Base(BaseModel):
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

    AnzahlFallNeu_7_Tage_Dropped: int = Field(alias="AnzahlFallNeu-7-Tage-Dropped")
    AnzahlTodesfallNeu_7_Tage: int = Field(alias="AnzahlFallNeu-7-Tage-Dropped")
    Fallsterblichkeit_Prozent: float = Field(alias="Fallsterblichkeit-Prozent")
    Kontaktrisiko: float
    InzidenzFallNeu_7_Tage: float = Field(alias="InzidenzFallNeu-7-Tage")
    MeldeDauerFallNeu_Schnitt: float = Field(alias="MeldeDauerFallNeu-Schnitt")
    InzidenzFallNeu_7_Tage_Trend_Spezial: float = Field(alias="InzidenzFallNeu-7-Tage-Trend-Spezial")
    Kehrwert_risiko: float

    class Config:
        orm_mode = True
