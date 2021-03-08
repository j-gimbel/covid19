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

    Name = Column(String, nullable=False)

    # down
    landkreise = relationship("Landkreis", back_populates="bundesland")
    daten_nach_meldedatum = relationship(
        "Bundesland_Daten_Nach_Meldedatum", back_populates="bundesland"
    )

    alle_faelle = relationship("Fall_Daten_Taeglich", back_populates="bundesland")


class Bundesland_Daten_Nach_Meldedatum(Base):
    __tablename__ = "bundeslaender_daten_nach_meldedatum"
    __table_args__ = (UniqueConstraint("ID", "MeldeDatum"),)
    ID = Column(Integer, primary_key=True, index=True)
    MeldeDatum = Column(Integer, nullable=False)
    AnzahlFall = Column(Integer, nullable=False)
    AnzahlTodesfall = Column(Integer, nullable=False)
    AnzahlGenesen = Column(Integer, nullable=False)
    Bevoelkerung = Column(Integer, nullable=False)
    FaellePro100k = Column(Integer, nullable=False)
    TodesfaellePro100k = Column(Integer, nullable=False)

    # up
    bundesland_id = Column(Integer, ForeignKey("bundeslaender.ID"))
    bundesland = relationship(
        "Bundesland", back_populates="daten_nach_meldedatum", lazy="joined"
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
    Name = Column(String, nullable=False)
    Typ = Column(String, nullable=False)
    Bevoelkerung = Column(Integer, nullable=False)

    # up
    BL_ID = Column(Integer, ForeignKey("bundeslaender.ID"))
    bundesland = relationship("Bundesland", back_populates="landkreise")

    # down

    daten_nach_meldedatum = relationship(
        "Landkreis_Daten_Nach_Meldedatum", back_populates="landkreis"
    )

    alle_faelle = relationship("Fall_Daten_Taeglich", back_populates="landkreis")


class Landkreis_Daten_Nach_Meldedatum(Base):
    __tablename__ = "landkreise_daten_nach_meldedatum"
    ID = Column(Integer, primary_key=True, index=True)
    MeldeDatum = Column(Integer, nullable=False)
    AnzahlFall = Column(Integer, nullable=False)
    AnzahlTodesfall = Column(Integer, nullable=False)
    AnzahlGenesen = Column(Integer, nullable=False)
    Bevoelkerung = Column(Integer, nullable=False)
    FaellePro100k = Column(Integer, nullable=False)
    TodesfaellePro100k = Column(Integer, nullable=False)

    # up
    landkreis_id = Column(Integer, ForeignKey("landkreise.ID"))
    landkreis = relationship("Landkreis", back_populates="daten_nach_meldedatum")

    Altersgruppe_id = Column(Integer, ForeignKey("altersgruppen.id"))
    Altersgruppe = relationship("Altersgruppe", back_populates="landkreis_faelle")


class Altersgruppe(Base):
    __tablename__ = "altersgruppen"
    id = Column(Integer, primary_key=True, index=True)
    Name = Column(String, index=True)

    # down

    bundesland_faelle = relationship(
        "Bundesland_Daten_Nach_Meldedatum", back_populates="Altersgruppe"
    )

    landkreis_faelle = relationship(
        "Landkreis_Daten_Nach_Meldedatum", back_populates="Altersgruppe"
    )

    alle_faelle = relationship("Fall_Daten_Taeglich", back_populates="Altersgruppe")


class Fall_Daten_Taeglich(Base):
    __tablename__ = "faelle_daten_taeglich"
    # __table_args__ = (UniqueConstraint("name", "typ", name="_lk_name_typ_uc"),)
    ID = Column(Integer, primary_key=True, index=True)
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
    Altersgruppe_id = Column(Integer, ForeignKey("altersgruppen.id"))
    Altersgruppe = relationship("Altersgruppe", back_populates="alle_faelle")

    landkreis_id = Column(Integer, ForeignKey("landkreise.ID"))
    landkreis = relationship("Landkreis", back_populates="alle_faelle")

    bundesland_id = Column(Integer, ForeignKey("bundeslaender.ID"))
    bundesland = relationship("Bundesland", back_populates="alle_faelle")

    bundesland_meldedatum_id = Column(
        Integer, ForeignKey("bundeslaender_daten_nach_meldedatum.ID")
    )
    bundesland_meldedatum = relationship(
        "Bundesland_Daten_Nach_Meldedatum", back_populates="Zugehoerige_faelle"
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
