"""login_failures table for the login rate limit (D30)

Revision ID: 0002
Revises: 0001
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import TIMESTAMP

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "login_failures",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column("username", sa.Text, nullable=False),
        sa.Column("ip", sa.Text, nullable=False),
        sa.Column("failed_at", TIMESTAMP(timezone=True), nullable=False),
    )
    op.create_index("ix_login_failures_username_failed_at", "login_failures", ["username", "failed_at"])
    op.create_index("ix_login_failures_ip_failed_at", "login_failures", ["ip", "failed_at"])
    op.create_index("ix_login_failures_failed_at", "login_failures", ["failed_at"])


def downgrade() -> None:
    op.drop_table("login_failures")
