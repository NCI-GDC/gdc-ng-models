"""add start end datetimes for notifications

Revision ID: e9d53a640d5d
Revises:
Create Date: 2020-12-11 16:06:21.960486

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e9d53a640d5d"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "notifications",
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "notifications",
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade():
    op.drop_column("notifications", "start_date")
    op.drop_column("notifications", "end_date")
