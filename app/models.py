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

    flaeche = Column(Float)
    dichte = Column(Float)
    einwohner = Column(Integer)

    # down
    bundeslaender = relationship("Bundesland", back_populates="bundesrepublik")
    daten = relationship("Bundesrepublik_Daten", back_populates="bundesrepublik")

class Bundesrepublik_Daten(Base):
    __tablename__ = "bundesrepublik_daten"
    ID = Column(Integer, primary_key=True, index=True)

    DatenstandTag = Column(Integer)
    Datum = Column(String)
    AnzahlFall = Column(Integer)
    AnzahlFallNeu = Column(Integer)
    AnzahlTodesfall = Column(Integer)
    AnzahlTodesfallNeu = Column(Integer)
    AnzahlGenesen = Column(Integer)
    AnzahlGenesenNeu = Column(Integer)
    InzidenzFallNeu = Column(Float)
    InzidenzTodesfallNeu = Column(Float)
    InzidenzFall = Column(Float)
    InzidenzTodesfall = Column(Float)
    AnzahlFallNeu_7_Tage = Column(Integer)
    AnzahlFallNeu_7_Tage_Trend = Column(Float)
    AnzahlFallNeu_7_Tage_7_Tage_davor = Column(Integer)
    AnzahlTodesfallNeu_7_Tage = Column(Integer)
    AnzahlTodesfallNeu_7_Tage_Trend = Column(Float)
    AnzahlTodesfallNeu_7_Tage_7_Tage_davor = Column(Integer)
    AnzahlGenesenNeu_7_Tage = Column(Integer)
    AnzahlGenesenNeu_7_Tage_Trend = Column(Float)
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

    # up
    bundesrepublik_id = Column(Integer, ForeignKey("bundesrepublik.ID"))
    bundesrepublik = relationship(
        "Bundesrepublik", back_populates="daten", lazy="joined"
    )


class Bundesland(Base):
    __tablename__ = "bundeslaender"
    ID = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    flaeche = Column(Float)
    dichte = Column(Float)
    einwohner = Column(Integer)

    # up
    BR_ID = Column(Integer, ForeignKey("bundesrepublik.ID"))
    bundesrepublik = relationship("Bundesrepublik", back_populates="bundeslaender")

    # down
    landkreise = relationship("Landkreis", back_populates="bundesland")
    daten = relationship(
        "Bundesland_Daten", back_populates="bundesland"
    )
    Bevoelkerung = Column(Integer, nullable=False)

    alle_faelle = relationship("Fall_Daten_Taeglich", back_populates="bundesland")


class Bundesland_Daten(Base):
    __tablename__ = "bundeslaender_daten"
    # __table_args__ = (UniqueConstraint("ID", "MeldeDatum"),)
    ID = Column(Integer, primary_key=True, index=True)

    DatenstandTag = Column(Integer)
    Datum = Column(String)
    AnzahlFall = Column(Integer)
    AnzahlFallNeu = Column(Integer)
    AnzahlTodesfall = Column(Integer)
    AnzahlTodesfallNeu = Column(Integer)
    AnzahlGenesen = Column(Integer)
    AnzahlGenesenNeu = Column(Integer)
    InzidenzFallNeu = Column(Float)
    InzidenzTodesfallNeu = Column(Float)
    InzidenzFall = Column(Float)
    InzidenzTodesfall = Column(Float)
    AnzahlFallNeu_7_Tage = Column(Integer)
    AnzahlFallNeu_7_Tage_Trend = Column(Float)
    AnzahlFallNeu_7_Tage_7_Tage_davor = Column(Integer)
    AnzahlTodesfallNeu_7_Tage = Column(Integer)
    AnzahlTodesfallNeu_7_Tage_Trend = Column(Float)
    AnzahlTodesfallNeu_7_Tage_7_Tage_davor = Column(Integer)
    AnzahlGenesenNeu_7_Tage = Column(Integer)
    AnzahlGenesenNeu_7_Tage_Trend = Column(Float)
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

    # up
    bundesland_id = Column(Integer, ForeignKey("bundeslaender.ID"))
    bundesland = relationship(
        "Bundesland", back_populates="daten", lazy="joined"
    )

    Altersgruppe_id = Column(Integer, ForeignKey("altersgruppen.id"))
    Altersgruppe = relationship("Altersgruppe", back_populates="bundesland_faelle")

    # down

    Zugehoerige_faelle = relationship(
        "Fall_Daten_Taeglich", back_populates="bundesland_meldedatum"
    )


class Landkreis(Base):
    __tablename__ = "landkreise"
    # __table_args__ = (UniqueConstraint("name", "typ", name="_lk_name_typ_uc"),)
    ID = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    typ = Column(String, nullable=False)
    flaeche = Column(Float)
    dichte = Column(Float)
    einwohner = Column(Integer)

    # up
    BL_ID = Column(Integer, ForeignKey("bundeslaender.ID"))
    bundesland = relationship("Bundesland", back_populates="landkreise")

    # down

    daten = relationship(
        "Landkreis_Daten", back_populates="landkreis"
    )

    alle_faelle = relationship("Fall_Daten_Taeglich", back_populates="landkreis")


class Landkreis_Daten(Base):
    __tablename__ = "landkreise_daten"
    ID = Column(Integer, primary_key=True, index=True)

    DatenstandTag = Column(Integer)
    Datum = Column(String)
    AnzahlFall = Column(Integer)
    AnzahlFallNeu = Column(Integer)
    AnzahlTodesfall = Column(Integer)
    AnzahlTodesfallNeu = Column(Integer)
    AnzahlGenesen = Column(Integer)
    AnzahlGenesenNeu = Column(Integer)
    InzidenzFallNeu = Column(Float)
    InzidenzTodesfallNeu = Column(Float)
    InzidenzFall = Column(Float)
    InzidenzTodesfall = Column(Float)
    AnzahlFallNeu_7_Tage = Column(Integer)
    AnzahlFallNeu_7_Tage_Trend = Column(Float)
    AnzahlFallNeu_7_Tage_7_Tage_davor = Column(Integer)
    AnzahlTodesfallNeu_7_Tage = Column(Integer)
    AnzahlTodesfallNeu_7_Tage_Trend = Column(Float)
    AnzahlTodesfallNeu_7_Tage_7_Tage_davor = Column(Integer)
    AnzahlGenesenNeu_7_Tage = Column(Integer)
    AnzahlGenesenNeu_7_Tage_Trend = Column(Float)
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

    # up
    landkreis_id = Column(Integer, ForeignKey("landkreise.ID"))
    landkreis = relationship("Landkreis", back_populates="daten")

    Altersgruppe_id = Column(Integer, ForeignKey("altersgruppen.id"))
    Altersgruppe = relationship("Altersgruppe", back_populates="landkreis_faelle")


class Altersgruppe(Base):
    __tablename__ = "altersgruppen"
    id = Column(Integer, primary_key=True, index=True)
    Name = Column(String, index=True)

    # down

    bundesland_faelle = relationship(
        "Bundesland_Daten", back_populates="Altersgruppe"
    )

    landkreis_faelle = relationship(
        "Landkreis_Daten", back_populates="Altersgruppe"
    )

    alle_faelle = relationship("Fall_Daten_Taeglich", back_populates="Altersgruppe")


class Fall_Daten_Taeglich(Base):
    __tablename__ = "faelle_daten_taeglich"
    # __table_args__ = (UniqueConstraint("name", "typ", name="_lk_name_typ_uc"),)
    ID = Column(Integer, primary_key=True, index=True)

    Geschlecht = Column(String)
    MeldeDatum = Column(Integer, nullable=False, index=True)
    AnzahlFall = Column(Integer, nullable=False)
    AnzahlTodesfall = Column(Integer, nullable=False)
    AnzahlGenesen = Column(Integer, nullable=False)

    # Pavel
    """
    caseHash = Column(BigInteger)
    msgHash = Column(BigInteger)
    refDay = Column(Integer)
    meldeDay = Column(Integer)
    neuerFallKlar = Column(String)  # neuerFallGesternUndHeute / neuerFallNurHeute
    newBeforeDay = Column(Integer)
    newCaseBeforeDay = Column(Integer)
    anzahlFallLfd = Column(Integer)  # summe der Fälle
    anzahlTodesFallLfd = Column(Integer)  # summe der Fälle

    faellePro100k = Column(Float)  # kannn man dass nicht berechnen ?
    isStadt = Column(Boolean)  # 0/1
    erkDay = Column(Integer)
    newCaseOnDay = Column(Integer)
    newOnDay = Column(Integer)
    caseDelay = Column(Integer)
    NeuerTodesfallKlar = Column(String)  # neuerTodesfallGesternUndHeute /
    newDeathBeforeDay = Column(Integer)
    newDeathOnDay = Column(Integer)
    deathDelay = Column(Integer)
    missingSinceDay = Column(Integer)
    missingCasesInOldRecord = Column(Integer)
    poppedUpOnDay = Column(Integer)
    """
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


class Inserted_csv_File(Base):

    __tablename__ = "inserted_csv_files"
    # __table_args__ = (UniqueConstraint("name", "typ", name="_lk_name_typ_uc"),)
    ID = Column(Integer, primary_key=True, index=True)
    data_type = Column(String)
    date = Column(String)
    md5sum = Column(String)
    file_path = Column(String)
    date_file_processed = Column(String)
