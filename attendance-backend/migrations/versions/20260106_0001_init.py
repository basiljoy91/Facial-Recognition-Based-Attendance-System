"""initial schema with pgvector"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision = "20260106_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(length=64), nullable=False, unique=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("roll_no", sa.String(length=64), nullable=True),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_external_id", "users", ["external_id"])
    op.create_index("ix_users_roll_no", "users", ["roll_no"])

    op.create_table(
        "model_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=64), nullable=False, unique=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )

    op.create_table(
        "face_embeddings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("model_version", sa.String(length=64), nullable=False),
        sa.Column("vector", Vector(512), nullable=False),
        sa.Column("encrypted_blob", sa.LargeBinary(), nullable=False),
        sa.Column("liveness_score", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "model_version", name="uq_user_model"),
    )
    op.create_index("ix_face_embeddings_user_id", "face_embeddings", ["user_id"])
    op.create_index("ix_face_embeddings_vector", "face_embeddings", ["vector"], postgresql_using="ivfflat")

    op.create_table(
        "attendance_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("type", sa.String(length=16), nullable=False),
        sa.Column("timestamp", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("confidence", sa.Integer(), nullable=False),
        sa.Column("liveness_score", sa.Integer(), nullable=True),
        sa.Column("manual_override", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("extra_data", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.UniqueConstraint("user_id", "date", "type", name="uq_user_date_type"),
    )
    op.create_index("ix_attendance_user_id", "attendance_logs", ["user_id"])
    op.create_index("ix_attendance_timestamp", "attendance_logs", ["timestamp"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("entity", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.String(length=64), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )


def downgrade():
    op.drop_table("audit_logs")
    op.drop_index("ix_attendance_timestamp", table_name="attendance_logs")
    op.drop_index("ix_attendance_user_id", table_name="attendance_logs")
    op.drop_table("attendance_logs")
    op.drop_index("ix_face_embeddings_vector", table_name="face_embeddings")
    op.drop_index("ix_face_embeddings_user_id", table_name="face_embeddings")
    op.drop_table("face_embeddings")
    op.drop_table("model_versions")
    op.drop_index("ix_users_roll_no", table_name="users")
    op.drop_index("ix_users_external_id", table_name="users")
    op.drop_table("users")
    op.execute("DROP EXTENSION IF EXISTS vector")

