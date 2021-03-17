from sqlalchemy import (
    Boolean,
    Float,
    Column,
    ForeignKey,
    Integer,
    BigInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from .database import Base


class Bundesrepublik(Base):
    __tablename__ = "bundesrepublik"
    ID = Column(Integer, primary_key=True, index=True)

    Flaeche = Column(Float)
    Dichte = Column(Float)
    Einwohner = Column(Integer)

    # down
    Bundeslaender = relationship("Bundesland", back_populates="Bundesrepublik")
    Daten = relationship("Bundesrepublik_Daten", back_populates="Bundesrepublik")

class Bundesrepublik_Daten(Base):
    __tablename__ = "bundesrepublik_daten"
    ID = Column(Integer, primary_key=True, index=True)

    DatenstandTag = Column(Integer)
    Datum = Column(String, index=True)
    AnzahlFall = Column(Integer)
    AnzahlFallNeu = Column(Integer)
    AnzahlTodesfall = Column(Integer)
    AnzahlTodesfallNeu = Column(Integer)
    AnzahlGenesen = Column(Integer)
    AnzahlGenesenNeu = Column(Integer)

    AnzahlFallNeu_Meldung_letze_7_Tage = Column(Integer)
    AnzahlFallNeu_Meldung_letze_14_Tage = Column(Integer)
    MeldeDauerFallNeu_Min = Column(Integer)
    MeldeDauerFallNeu_Max = Column(Integer)
    MeldeDauerFallNeu_Schnitt = Column(Float)
    MeldeDauerFallNeu_Median = Column(Float)
    MeldeDauerFallNeu_StdAbw = Column(Float)
    MeldeDauerFallNeu_Fallbasis = Column(Integer)
    DatenstandTag_Max = Column(Integer)

    InzidenzFallNeu = Column(Float)
    InzidenzTodesfallNeu = Column(Float)
    InzidenzFall = Column(Float)
    InzidenzTodesfall = Column(Float)

    Fallsterblichkeit_Prozent = Column(Float)

    AnzahlFallNeu_7_Tage = Column(Integer)
    AnzahlFallNeu_7_Tage_Trend = Column(Float)
    AnzahlFallNeu_7_Tage_7_Tage_davor = Column(Integer)
    AnzahlTodesfallNeu_7_Tage = Column(Integer)
    AnzahlTodesfallNeu_7_Tage_Trend = Column(Float)
    AnzahlTodesfallNeu_7_Tage_7_Tage_davor = Column(Integer)
    AnzahlGenesenNeu_7_Tage = Column(Integer)
    AnzahlGenesenNeu_7_Tage_Trend = Column(Float)

    AnzahlFallNeu_Meldung_letze_7_Tage_7_Tage = Column(Integer)
    AnzahlFallNeu_Meldung_letze_7_Tage_7_Tage_Trend = Column(Float)
    AnzahlFallNeu_Meldung_letze_14_Tage_7_Tage = Column(Integer)
    AnzahlFallNeu_Meldung_letze_14_Tage_7_Tage_Trend = Column(Float)
    MeldeDauerFallNeu_Min_7_Tage = Column(Integer)
    MeldeDauerFallNeu_Min_7_Tage_Trend = Column(Float)
    MeldeDauerFallNeu_Max_7_Tage = Column(Integer)
    MeldeDauerFallNeu_Max_7_Tage_Trend = Column(Float)
    MeldeDauerFallNeu_Schnitt_7_Tage = Column(Float)
    MeldeDauerFallNeu_Schnitt_7_Tage_Trend = Column(Float)
    MeldeDauerFallNeu_Median_7_Tage = Column(Float)
    MeldeDauerFallNeu_Median_7_Tage_Trend = Column(Float)
    MeldeDauerFallNeu_StdAbw_7_Tage = Column(Float)
    MeldeDauerFallNeu_StdAbw_7_Tage_Trend = Column(Float)
    MeldeDauerFallNeu_Fallbasis_7_Tage = Column(Integer)
    MeldeDauerFallNeu_Fallbasis_7_Tage_Trend = Column(Float)

    InzidenzFallNeu_7_Tage = Column(Float)
    InzidenzFallNeu_7_Tage_Trend = Column(Float)
    InzidenzFallNeu_7_Tage_7_Tage_davor = Column(Float)
    InzidenzFallNeu_7_Tage_Trend_Spezial = Column(Float)
    InzidenzFallNeu_7_Tage_R = Column(Float)
    InzidenzFallNeu_Prognose_1_Wochen = Column(Float)
    InzidenzFallNeu_Prognose_2_Wochen = Column(Float)
    InzidenzFallNeu_Prognose_4_Wochen = Column(Float)
    InzidenzFallNeu_Prognose_8_Wochen = Column(Float)
    InzidenzFallNeu_Tage_bis_50 = Column(Float)
    InzidenzFallNeu_Tage_bis_100 = Column(Float)
    Kontaktrisiko = Column(Float)
    InzidenzTodesfallNeu_7_Tage = Column(Float)
    InzidenzTodesfallNeu_7_Tage_Trend = Column(Float)
    InzidenzTodesfallNeu_7_Tage_7_Tage_davor = Column(Float)
    InzidenzTodesfallNeu_7_Tage_Trend_Spezial = Column(Float)

    DatenstandTag_Diff = Column(Integer)
    InzidenzFallNeu_Meldung_letze_7_Tage_7_Tage = Column(Float)
    AnzahlFallNeu_7_Tage_Dropped = Column(Integer)
    ProzentFallNeu_7_Tage_Dropped = Column(Float)
    MeldeDauerFallNeu_Min_Neg = Column(Integer)

    # up
    Bundesrepublik_ID = Column(Integer, ForeignKey("bundesrepublik.ID"))
    Bundesrepublik = relationship(
        "Bundesrepublik", back_populates="Daten", lazy="joined"
    )


class Bundesland(Base):
    __tablename__ = "bundeslaender"
    ID = Column(Integer, primary_key=True, index=True)

    Name = Column(String, nullable=False)
    Kuerzel = Column(String, nullable=False)
    Flaeche = Column(Float)
    Dichte = Column(Float)
    Einwohner = Column(Integer)

    # up
    BR_ID = Column(Integer, ForeignKey("bundesrepublik.ID"))
    Bundesrepublik = relationship("Bundesrepublik", back_populates="Bundeslaender")

    # down
    Landkreise = relationship("Landkreis", back_populates="Bundesland")
    Daten = relationship(
        "Bundesland_Daten", back_populates="Bundesland"
    )

    # alle_faelle = relationship("Fall_Daten_Taeglich", back_populates="bundesland")


class Bundesland_Daten(Base):
    __tablename__ = "bundeslaender_daten"
    # __table_args__ = (UniqueConstraint("ID", "MeldeDatum"),)
    ID = Column(Integer, primary_key=True, index=True)

    DatenstandTag = Column(Integer)
    Datum = Column(String, index=True)
    AnzahlFall = Column(Integer)
    AnzahlFallNeu = Column(Integer)
    AnzahlTodesfall = Column(Integer)
    AnzahlTodesfallNeu = Column(Integer)
    AnzahlGenesen = Column(Integer)
    AnzahlGenesenNeu = Column(Integer)

    AnzahlFallNeu_Meldung_letze_7_Tage = Column(Integer)
    AnzahlFallNeu_Meldung_letze_14_Tage = Column(Integer)
    MeldeDauerFallNeu_Min = Column(Integer)
    MeldeDauerFallNeu_Max = Column(Integer)
    MeldeDauerFallNeu_Schnitt = Column(Float)
    MeldeDauerFallNeu_Median = Column(Float)
    MeldeDauerFallNeu_StdAbw = Column(Float)
    MeldeDauerFallNeu_Fallbasis = Column(Integer)
    DatenstandTag_Max = Column(Integer)

    InzidenzFallNeu = Column(Float)
    InzidenzTodesfallNeu = Column(Float)
    InzidenzFall = Column(Float)
    InzidenzTodesfall = Column(Float)

    Fallsterblichkeit_Prozent = Column(Float)

    AnzahlFallNeu_7_Tage = Column(Integer)
    AnzahlFallNeu_7_Tage_Trend = Column(Float)
    AnzahlFallNeu_7_Tage_7_Tage_davor = Column(Integer)
    AnzahlTodesfallNeu_7_Tage = Column(Integer)
    AnzahlTodesfallNeu_7_Tage_Trend = Column(Float)
    AnzahlTodesfallNeu_7_Tage_7_Tage_davor = Column(Integer)
    AnzahlGenesenNeu_7_Tage = Column(Integer)
    AnzahlGenesenNeu_7_Tage_Trend = Column(Float)

    AnzahlFallNeu_Meldung_letze_7_Tage_7_Tage = Column(Integer)
    AnzahlFallNeu_Meldung_letze_7_Tage_7_Tage_Trend = Column(Float)
    AnzahlFallNeu_Meldung_letze_14_Tage_7_Tage = Column(Integer)
    AnzahlFallNeu_Meldung_letze_14_Tage_7_Tage_Trend = Column(Float)
    MeldeDauerFallNeu_Min_7_Tage = Column(Integer)
    MeldeDauerFallNeu_Min_7_Tage_Trend = Column(Float)
    MeldeDauerFallNeu_Max_7_Tage = Column(Integer)
    MeldeDauerFallNeu_Max_7_Tage_Trend = Column(Float)
    MeldeDauerFallNeu_Schnitt_7_Tage = Column(Float)
    MeldeDauerFallNeu_Schnitt_7_Tage_Trend = Column(Float)
    MeldeDauerFallNeu_Median_7_Tage = Column(Float)
    MeldeDauerFallNeu_Median_7_Tage_Trend = Column(Float)
    MeldeDauerFallNeu_StdAbw_7_Tage = Column(Float)
    MeldeDauerFallNeu_StdAbw_7_Tage_Trend = Column(Float)
    MeldeDauerFallNeu_Fallbasis_7_Tage = Column(Integer)
    MeldeDauerFallNeu_Fallbasis_7_Tage_Trend = Column(Float)

    InzidenzFallNeu_7_Tage = Column(Float)
    InzidenzFallNeu_7_Tage_Trend = Column(Float)
    InzidenzFallNeu_7_Tage_7_Tage_davor = Column(Float)
    InzidenzFallNeu_7_Tage_Trend_Spezial = Column(Float)
    InzidenzFallNeu_7_Tage_R = Column(Float)
    InzidenzFallNeu_Prognose_1_Wochen = Column(Float)
    InzidenzFallNeu_Prognose_2_Wochen = Column(Float)
    InzidenzFallNeu_Prognose_4_Wochen = Column(Float)
    InzidenzFallNeu_Prognose_8_Wochen = Column(Float)
    InzidenzFallNeu_Tage_bis_50 = Column(Float)
    InzidenzFallNeu_Tage_bis_100 = Column(Float)
    Kontaktrisiko = Column(Float)
    InzidenzTodesfallNeu_7_Tage = Column(Float)
    InzidenzTodesfallNeu_7_Tage_Trend = Column(Float)
    InzidenzTodesfallNeu_7_Tage_7_Tage_davor = Column(Float)
    InzidenzTodesfallNeu_7_Tage_Trend_Spezial = Column(Float)

    DatenstandTag_Diff = Column(Integer)
    InzidenzFallNeu_Meldung_letze_7_Tage_7_Tage = Column(Float)
    AnzahlFallNeu_7_Tage_Dropped = Column(Integer)
    ProzentFallNeu_7_Tage_Dropped = Column(Float)
    MeldeDauerFallNeu_Min_Neg = Column(Integer)

    # up
    Bundesland_ID = Column(Integer, ForeignKey("bundeslaender.ID"))
    Bundesland = relationship(
        "Bundesland", back_populates="Daten", lazy="joined"
    )

    Altersgruppe_id = Column(Integer, ForeignKey("altersgruppen.ID"))
    Altersgruppe = relationship("Altersgruppe", back_populates="Bundesland_faelle")

    # down

    # Zugehoerige_faelle = relationship("Fall_Daten_Taeglich", back_populates="bundesland_meldedatum")


class Landkreis(Base):
    __tablename__ = "landkreise"
    # __table_args__ = (UniqueConstraint("name", "typ", name="_lk_name_typ_uc"),)
    ID = Column(Integer, primary_key=True, index=True)

    Name = Column(String, nullable=False, index=True)
    Typ = Column(String, nullable=False)
    Flaeche = Column(Float)
    Dichte = Column(Float)
    Einwohner = Column(Integer)

    # up
    BL_ID = Column(Integer, ForeignKey("bundeslaender.ID"))
    Bundesland = relationship("Bundesland", back_populates="Landkreise")

    # down

    Daten = relationship(
        "Landkreis_Daten", back_populates="Landkreis"
    )

    # alle_faelle = relationship("Fall_Daten_Taeglich", back_populates="landkreis")


class Landkreis_Daten(Base):
    __tablename__ = "landkreise_daten"
    ID = Column(Integer, primary_key=True, index=True)

    DatenstandTag = Column(Integer)
    Datum = Column(String, index=True)
    AnzahlFall = Column(Integer)
    AnzahlFallNeu = Column(Integer)
    AnzahlTodesfall = Column(Integer)
    AnzahlTodesfallNeu = Column(Integer)
    AnzahlGenesen = Column(Integer)
    AnzahlGenesenNeu = Column(Integer)

    AnzahlFallNeu_Meldung_letze_7_Tage = Column(Integer)
    AnzahlFallNeu_Meldung_letze_14_Tage = Column(Integer)
    MeldeDauerFallNeu_Min = Column(Integer)
    MeldeDauerFallNeu_Max = Column(Integer)
    MeldeDauerFallNeu_Schnitt = Column(Float)
    MeldeDauerFallNeu_Median = Column(Float)
    MeldeDauerFallNeu_StdAbw = Column(Float)
    MeldeDauerFallNeu_Fallbasis = Column(Integer)
    DatenstandTag_Max = Column(Integer)

    InzidenzFallNeu = Column(Float)
    InzidenzTodesfallNeu = Column(Float)
    InzidenzFall = Column(Float)
    InzidenzTodesfall = Column(Float)

    Fallsterblichkeit_Prozent = Column(Float)

    AnzahlFallNeu_7_Tage = Column(Integer)
    AnzahlFallNeu_7_Tage_Trend = Column(Float)
    AnzahlFallNeu_7_Tage_7_Tage_davor = Column(Integer)
    AnzahlTodesfallNeu_7_Tage = Column(Integer)
    AnzahlTodesfallNeu_7_Tage_Trend = Column(Float)
    AnzahlTodesfallNeu_7_Tage_7_Tage_davor = Column(Integer)
    AnzahlGenesenNeu_7_Tage = Column(Integer)
    AnzahlGenesenNeu_7_Tage_Trend = Column(Float)

    AnzahlFallNeu_Meldung_letze_7_Tage_7_Tage = Column(Integer)
    AnzahlFallNeu_Meldung_letze_7_Tage_7_Tage_Trend = Column(Float)
    AnzahlFallNeu_Meldung_letze_14_Tage_7_Tage = Column(Integer)
    AnzahlFallNeu_Meldung_letze_14_Tage_7_Tage_Trend = Column(Float)
    MeldeDauerFallNeu_Min_7_Tage = Column(Integer)
    MeldeDauerFallNeu_Min_7_Tage_Trend = Column(Float)
    MeldeDauerFallNeu_Max_7_Tage = Column(Integer)
    MeldeDauerFallNeu_Max_7_Tage_Trend = Column(Float)
    MeldeDauerFallNeu_Schnitt_7_Tage = Column(Float)
    MeldeDauerFallNeu_Schnitt_7_Tage_Trend = Column(Float)
    MeldeDauerFallNeu_Median_7_Tage = Column(Float)
    MeldeDauerFallNeu_Median_7_Tage_Trend = Column(Float)
    MeldeDauerFallNeu_StdAbw_7_Tage = Column(Float)
    MeldeDauerFallNeu_StdAbw_7_Tage_Trend = Column(Float)
    MeldeDauerFallNeu_Fallbasis_7_Tage = Column(Integer)
    MeldeDauerFallNeu_Fallbasis_7_Tage_Trend = Column(Float)

    InzidenzFallNeu_7_Tage = Column(Float)
    InzidenzFallNeu_7_Tage_Trend = Column(Float)
    InzidenzFallNeu_7_Tage_7_Tage_davor = Column(Float)
    InzidenzFallNeu_7_Tage_Trend_Spezial = Column(Float)
    InzidenzFallNeu_7_Tage_R = Column(Float)
    InzidenzFallNeu_Prognose_1_Wochen = Column(Float)
    InzidenzFallNeu_Prognose_2_Wochen = Column(Float)
    InzidenzFallNeu_Prognose_4_Wochen = Column(Float)
    InzidenzFallNeu_Prognose_8_Wochen = Column(Float)
    InzidenzFallNeu_Tage_bis_50 = Column(Float)
    InzidenzFallNeu_Tage_bis_100 = Column(Float)
    Kontaktrisiko = Column(Float)
    InzidenzTodesfallNeu_7_Tage = Column(Float)
    InzidenzTodesfallNeu_7_Tage_Trend = Column(Float)
    InzidenzTodesfallNeu_7_Tage_7_Tage_davor = Column(Float)
    InzidenzTodesfallNeu_7_Tage_Trend_Spezial = Column(Float)

    DatenstandTag_Diff = Column(Integer)
    InzidenzFallNeu_Meldung_letze_7_Tage_7_Tage = Column(Float)
    AnzahlFallNeu_7_Tage_Dropped = Column(Integer)
    ProzentFallNeu_7_Tage_Dropped = Column(Float)
    MeldeDauerFallNeu_Min_Neg = Column(Integer)

    # up
    Landkreis_ID = Column(Integer, ForeignKey("landkreise.ID"))
    Landkreis = relationship("Landkreis", back_populates="Daten")

    Altersgruppe_ID = Column(Integer, ForeignKey("altersgruppen.ID"))
    Altersgruppe = relationship("Altersgruppe", back_populates="Landkreis_faelle")


class Altersgruppe(Base):
    __tablename__ = "altersgruppen"
    ID = Column(Integer, primary_key=True, index=True)
    Name = Column(String, index=True)

    # down

    Bundesland_faelle = relationship(
        "Bundesland_Daten", back_populates="Altersgruppe"
    )

    Landkreis_faelle = relationship(
        "Landkreis_Daten", back_populates="Altersgruppe"
    )

    #alle_faelle = relationship("Fall_Daten_Taeglich", back_populates="Altersgruppe")


"""
class Fall_Daten_Taeglich(Base):
    __tablename__ = "faelle_daten_taeglich"
    # __table_args__ = (UniqueConstraint("name", "typ", name="_lk_name_typ_uc"),)
    ID = Column(Integer, primary_key=True, index=True)

    Geschlecht = Column(String)
    MeldeDatum = Column(Integer, nullable=False, index=True)
    AnzahlFall = Column(Integer, nullable=False)
    AnzahlTodesfall = Column(Integer, nullable=False)
    AnzahlGenesen = Column(Integer, nullable=False)

    
    # up
    Altersgruppe_id = Column(Integer, ForeignKey("altersgruppen.id"))
    Altersgruppe = relationship("Altersgruppe", back_populates="alle_faelle")

  
    landkreis_id = Column(Integer, ForeignKey("landkreise.ID"))
    landkreis = relationship("Landkreis", back_populates="alle_faelle")

    bundesland_id = Column(Integer, ForeignKey("bundeslaender.ID"))
    bundesland = relationship("Bundesland", back_populates="alle_faelle")

    bundesland_meldedatum_id = Column(
        Integer, ForeignKey("bundeslaender_daten.ID")
    )
    bundesland_meldedatum = relationship(
        "Bundesland_Daten", back_populates="Zugehoerige_faelle"
    )
"""


class Inserted_csv_File(Base):

    __tablename__ = "inserted_csv_files"
    # __table_args__ = (UniqueConstraint("name", "typ", name="_lk_name_typ_uc"),)
    ID = Column(Integer, primary_key=True, index=True)
    data_type = Column(String)
    date = Column(String)
    md5sum = Column(String)
    file_path = Column(String)
    date_file_processed = Column(String)
