import sqlalchemy as sa

from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "narasimha_patients",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("email_address", sa.String(length=255), nullable=False, unique=True),
        sa.Column("phone_number", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "narasimha_doctors",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("medical_specialization", sa.String(length=255), nullable=False),
        sa.Column(
            "active_status",
            sa.Boolean,
            server_default=sa.true(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "narasimha_appointments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "patient_id",
            sa.Integer,
            sa.ForeignKey("narasimha_patients.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "doctor_id",
            sa.Integer,
            sa.ForeignKey("narasimha_doctors.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "appointment_start_datetime",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("appointment_duration", sa.Integer, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_index(
        "idx_doctor_start_time",
        "narasimha_appointments",
        ["doctor_id", "appointment_start_datetime"],
    )


def downgrade():
    op.drop_index("idx_doctor_start_time", table_name="narasimha_appointments")
    op.drop_table("narasimha_appointments")
    op.drop_table("narasimha_doctors")
    op.drop_table("narasimha_patients")
