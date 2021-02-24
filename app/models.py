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
    OBJECTID_1 = Column(Integer, primary_key=True, index=True)
    LAN_ew_GEN = Column(String, unique=True, index=True)
    LAN_ew_BEZ = Column(String)
    LAN_ew_EWZ = Column(String)
    Fallzahl = Column(String)
    Aktualisierung = Column(String)
    faelle_100000_EW = Column(Float)
    Death = Column(Integer)
    cases7_bl_per_100k = Column(Float)
    cases7_bl = Column(Float)
    death7_bl = Column(Float)

    # down
    landkreise = relationship("Landkreis", back_populates="bundesland")


class Landkreis(Base):
    __tablename__ = "landkreise"
    __table_args__ = (UniqueConstraint("name", "typ", name="_lk_name_typ_uc"),)
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    typ = Column(String, index=True)  # lk oder sk
    bevoelkerung = Column(Integer)

    # up
    bundesland_id = Column(Integer, ForeignKey("bundeslaender.OBJECTID_1"))
    bundesland = relationship("Bundesland", back_populates="landkreise")

    # down
    faelle = relationship("Fall", back_populates="landkreis")


class Altersgruppe(Base):
    __tablename__ = "altersgruppen"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    # down
    faelle_id = Column(Integer, ForeignKey("faelle.id"))
    faelle = relationship("Fall", back_populates="altersgruppe")


class Fall(Base):
    __tablename__ = "faelle"
    # __table_args__ = (UniqueConstraint("name", "typ", name="_lk_name_typ_uc"),)
    id = Column(Integer, primary_key=True, index=True)
    geschlecht = Column(String)
    anzahlFall = Column(Integer)
    anzahlTodesFall = Column(Integer)
    meldeDatum = Column(String)
    datenStand = Column(String)
    neuerFall = Column(Integer)  # 0/-1/-9
    neuerTodesFall = Column(Integer)  # 0/-1/-9
    refDatum = Column(String)
    neuGenesen = Column(Integer)  # 0/-1/-9
    anzahlGenesen = Column(Integer)  # 0/-1/-9
    anzahlGenesen = Column(Integer)  # 0/-1/-9
    istErkrankungsbeginn = Column(Boolean)  # 0/1
    altersgruppe2 = Column(String)

    # Pavel

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

    # up

    altersgruppe = relationship("Altersgruppe", back_populates="faelle")
    landkreis_id = Column(Integer, ForeignKey("landkreise.id"))
    landkreis = relationship("Landkreis", back_populates="faelle")
