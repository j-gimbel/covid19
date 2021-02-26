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


class Bundesland(Base):
    __tablename__ = "bundeslaender"
    ID = Column(Integer, primary_key=True, index=True)
    LAN_ew_GEN = Column(String, unique=True, index=True)
    LAN_ew_BEZ = Column(String)
    LAN_ew_EWZ = Column(String)

    # down
    landkreise = relationship("Landkreis", back_populates="bundesland")
    taegliche_daten = relationship(
        "Bundesland_Daten_Taeglich", back_populates="bundesland"
    )

    faelle = relationship("Fall", back_populates="bundesland")


class Bundesland_Daten_Taeglich(Base):
    __tablename__ = "bundeslaender_daten_taeglich"
    ID = Column(Integer, primary_key=True, index=True)
    Fallzahl = Column(String)
    Aktualisierung = Column(Integer)
    faelle_100000_EW = Column(Float)
    Death = Column(Integer)
    cases7_bl_per_100k = Column(Float)
    cases7_bl = Column(Float)
    death7_bl = Column(Float)

    # up
    bundesland_id = Column(Integer, ForeignKey("bundeslaender.ID"))
    bundesland = relationship("Bundesland", back_populates="taegliche_daten")


class Landkreis(Base):
    __tablename__ = "landkreise"
    # __table_args__ = (UniqueConstraint("name", "typ", name="_lk_name_typ_uc"),)
    ID = Column(Integer, primary_key=True, index=True)
    RS = Column(Integer)
    AGS = Column(Integer)
    GEN = Column(String, index=True)
    BEZ = Column(String)
    EWZ = Column(Integer)
    death_rate = Column(Float)
    cases = Column(Integer)
    deaths = Column(Integer)
    cases_per_100k = Column(Float)
    cases_per_population = Column(Float)
    county = Column(String, index=True)  # Landkreis name
    last_update = Column(Integer)
    cases7_per_100k = Column(Float)
    cases7_lk = Column(Integer)
    death7_lk = Column(Integer)

    # up
    BL_ID = Column(Integer, ForeignKey("bundeslaender.ID"))
    bundesland = relationship("Bundesland", back_populates="landkreise")

    # down
    faelle = relationship("Fall", back_populates="landkreis")


class Altersgruppe(Base):
    __tablename__ = "altersgruppen"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    # down

    faelle = relationship("Fall", back_populates="altersgruppe")


class Fall(Base):
    __tablename__ = "faelle"
    # __table_args__ = (UniqueConstraint("name", "typ", name="_lk_name_typ_uc"),)
    id = Column(Integer, primary_key=True, index=True)
    geschlecht = Column(String)
    anzahlFall = Column(Integer)
    anzahlTodesFall = Column(Integer)
    meldeDatum = Column(Integer)
    datenStand = Column(Integer)
    neuerFall = Column(Integer)  # 0/-1/-9
    neuerTodesFall = Column(Integer)  # 0/-1/-9
    refDatum = Column(Integer)
    neuGenesen = Column(Integer)  # 0/-1/-9
    anzahlGenesen = Column(Integer)  # 0/-1/-9
    istErkrankungsbeginn = Column(Boolean)  # 0/1
    altersgruppe2 = Column(String)

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
    altersgruppe_id = Column(Integer, ForeignKey("altersgruppen.id"))
    altersgruppe = relationship("Altersgruppe", back_populates="faelle")

    landkreis_id = Column(Integer, ForeignKey("landkreise.ID"))
    landkreis = relationship("Landkreis", back_populates="faelle")

    bundesland_id = Column(Integer, ForeignKey("bundeslaender.ID"))
    bundesland = relationship("Bundesland", back_populates="faelle")
