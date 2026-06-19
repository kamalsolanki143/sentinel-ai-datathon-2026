import uuid
import datetime
from typing import List, Optional
from enum import Enum as PyEnum
from sqlalchemy import String, Text, Float, Integer, Boolean, DateTime, Date, ForeignKey, Index, ARRAY, Enum
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class OfficerRole(str, PyEnum):
    admin = "admin"
    officer = "officer"
    analyst = "analyst"

class CriminalStatus(str, PyEnum):
    active = "active"
    arrested = "arrested"
    deceased = "deceased"
    absconding = "absconding"

class CrimeType(str, PyEnum):
    theft = "theft"
    cybercrime = "cybercrime"
    murder = "murder"
    assault = "assault"
    fraud = "fraud"
    kidnapping = "kidnapping"
    drug_trafficking = "drug_trafficking"
    vehicle_theft = "vehicle_theft"
    robbery = "robbery"
    other = "other"

class FIRStatus(str, PyEnum):
    open = "open"
    under_investigation = "under_investigation"
    closed = "closed"
    chargesheet_filed = "chargesheet_filed"

class ChatRole(str, PyEnum):
    user = "user"
    assistant = "assistant"

class Officer(Base):
    __tablename__ = "officers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    badge_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    rank: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[OfficerRole] = mapped_column(
        Enum(OfficerRole, name="officer_role_enum"),
        default=OfficerRole.officer,
        nullable=False
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )

    firs: Mapped[List["FIR"]] = relationship("FIR", back_populates="officer")
    chat_sessions: Mapped[List["ChatSession"]] = relationship("ChatSession", back_populates="officer")

class Criminal(Base):
    __tablename__ = "criminals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    aliases: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        default=list,
        nullable=False
    )
    dob: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    nationality: Mapped[str] = mapped_column(String(100), default="Indian", nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[CriminalStatus] = mapped_column(
        Enum(CriminalStatus, name="criminal_status_enum"),
        default=CriminalStatus.active,
        nullable=False
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False
    )

    firs: Mapped[List["CriminalFIR"]] = relationship("CriminalFIR", back_populates="criminal", cascade="all, delete-orphan")
    vehicles: Mapped[List["Vehicle"]] = relationship("Vehicle", back_populates="owner")
    phone_numbers: Mapped[List["PhoneNumber"]] = relationship("PhoneNumber", back_populates="criminal")
    known_locations: Mapped[List["KnownLocation"]] = relationship("KnownLocation", back_populates="criminal")

class FIR(Base):
    __tablename__ = "firs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    fir_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    date_filed: Mapped[datetime.datetime] = mapped_column(DateTime, index=True, nullable=False)
    crime_type: Mapped[CrimeType] = mapped_column(
        Enum(CrimeType, name="crime_type_enum"),
        index=True,
        nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location_lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    location_lng: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    location_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[FIRStatus] = mapped_column(
        Enum(FIRStatus, name="fir_status_enum"),
        default=FIRStatus.open,
        nullable=False
    )
    officer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("officers.id"), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )

    officer: Mapped["Officer"] = relationship("Officer", back_populates="firs")
    criminals: Mapped[List["CriminalFIR"]] = relationship("CriminalFIR", back_populates="fir", cascade="all, delete-orphan")

class CriminalFIR(Base):
    __tablename__ = "criminal_firs"

    criminal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("criminals.id", ondelete="CASCADE"), primary_key=True)
    fir_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("firs.id", ondelete="CASCADE"), primary_key=True)
    role_in_crime: Mapped[str] = mapped_column(String(100), default="suspect", nullable=False) # e.g. "accused", "witness", "suspect"

    criminal: Mapped["Criminal"] = relationship("Criminal", back_populates="firs")
    fir: Mapped["FIR"] = relationship("FIR", back_populates="criminals")

class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    registration_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    make: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    owner_criminal_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("criminals.id", ondelete="SET NULL"), nullable=True)

    owner: Mapped[Optional["Criminal"]] = relationship("Criminal", back_populates="vehicles")

class PhoneNumber(Base):
    __tablename__ = "phone_numbers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    number: Mapped[str] = mapped_column(String(20), nullable=False)
    criminal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("criminals.id", ondelete="CASCADE"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    criminal: Mapped["Criminal"] = relationship("Criminal", back_populates="phone_numbers")

class KnownLocation(Base):
    __tablename__ = "known_locations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    criminal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("criminals.id", ondelete="CASCADE"), nullable=False)
    location_name: Mapped[str] = mapped_column(String(255), nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    frequency_score: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    criminal: Mapped["Criminal"] = relationship("Criminal", back_populates="known_locations")

class CrimeHotspot(Base):
    __tablename__ = "crime_hotspots"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    district: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    crime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    prediction_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), default="v1.0", nullable=False)

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    officer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("officers.id"), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )

    officer: Mapped["Officer"] = relationship("Officer", back_populates="chat_sessions")
    messages: Mapped[List["ChatMessage"]] = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[ChatRole] = mapped_column(
        Enum(ChatRole, name="chat_role_enum"),
        nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )

    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")
