from typing import List, Optional

from pydantic import BaseModel


class Bundesland_Base(BaseModel):
    LAN_ew_GEN: str
    LAN_ew_EWZ: int

    class Config:
        orm_mode = True


class Bundesland_Daten_Taeglich_Base(BaseModel):

    Fallzahl: int
    Aktualisierung: int
    faelle_100000_EW: float
    Death: int
    cases7_bl_per_100k: float
    cases7_bl: float
    death7_bl: int


class Bundesland_Daten_Taeglich_Mit_Bundesland(BaseModel):
    Fallzahl: int
    Aktualisierung: int
    faelle_100000_EW: float
    Death: int
    cases7_bl_per_100k: float
    cases7_bl: int
    death7_bl: int
    bundesland: Bundesland_Base

    class Config:
        orm_mode = True