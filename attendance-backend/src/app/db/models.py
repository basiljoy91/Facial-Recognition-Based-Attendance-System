from datetime import datetime, timezone
from enum import Enum

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, LargeBinary, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON, TypeDecorator
from sqlalchemy.orm import relationship

from app.config import get_settings
from app.db.session import Base

settings = get_settings()


class EmbeddingVector(TypeDecorator):
    """
    Stores embeddings as pgvector on Postgres and JSON elsewhere for tests.
    """

    impl = Vector

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(Vector(settings.embedding_dim))
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value, dialect):
        return list(value) if value is not None else None

    def process_result_value(self, value, dialect):
        return value


class RoleEnum(str, Enum):
    ADMIN = "ADMIN"
    STAFF = "STAFF"
    STUDENT = "STUDENT"


class AttendanceTypeEnum(str, Enum):
    CLOCK_IN = "CLOCK_IN"
    CLOCK_OUT = "CLOCK_OUT"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(64), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    roll_no = Column(String(64), nullable=True, index=True)
    role = Column(String(16), nullable=False, default=RoleEnum.STUDENT.value)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    embeddings = relationship("FaceEmbedding", back_populates="user", cascade="all,delete-orphan")
    attendance_logs = relationship("AttendanceLog", back_populates="user", cascade="all,delete-orphan")


class FaceEmbedding(Base):
    __tablename__ = "face_embeddings"
    __table_args__ = (UniqueConstraint("user_id", "model_version", name="uq_user_model"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    model_version = Column(String(64), nullable=False, default="facenet_v1")
    vector = Column(EmbeddingVector(settings.embedding_dim), nullable=False)
    encrypted_blob = Column(LargeBinary, nullable=False)
    liveness_score = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="embeddings")


class AttendanceLog(Base):
    __tablename__ = "attendance_logs"
    __table_args__ = (UniqueConstraint("user_id", "date", "type", name="uq_user_date_type"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    type = Column(String(16), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    confidence = Column(Integer, nullable=False)
    liveness_score = Column(Integer, nullable=True)
    manual_override = Column(Boolean, nullable=False, default=False)
    extra_data = Column(JSONB, nullable=True)

    user = relationship("User", back_populates="attendance_logs")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(128), nullable=False)
    entity = Column(String(64), nullable=False)
    entity_id = Column(String(64), nullable=True)
    details = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, nullable=False, default=True)

