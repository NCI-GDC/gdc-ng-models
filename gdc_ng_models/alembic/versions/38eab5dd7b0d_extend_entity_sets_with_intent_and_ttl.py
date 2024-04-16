"""extend entity_sets with intent and ttl

Revision ID: 38eab5dd7b0d
Revises: 12dbbcac7a1d
Create Date: 2024-04-12 15:51:16.241332

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from gdc_ng_models.models import entity_set

# revision identifiers, used by Alembic.
revision = "38eab5dd7b0d"  # pragma: allowlist secret
down_revision = "12dbbcac7a1d"  # pragma: allowlist secret
branch_labels = None
depends_on = None


def upgrade():
    intent_type = postgresql.ENUM(
        "unknown", "internal", "external", "portal", "user", name="intent_type"
    )
    intent_type.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "entity_set",
        sa.Column(
            "intent_type",
            intent_type,
            server_default="unknown",
            comment="Provided by the client to provide a hint at the lifecycle of the entity_set",
            nullable=False,
        ),
    )
    op.add_column(
        "entity_set",
        sa.Column(
            "time_to_live_sec",
            sa.Integer(),
            comment="Provided by the client explicitly as to when this entity_set can be removed after inactivity",
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("entity_set", "time_to_live_sec")
    op.drop_column("entity_set", "intent_type")
    intent_type = postgresql.ENUM(
        "unknown", "internal", "external", "portal", "user", name="intent_type"
    )
    intent_type.drop(op.get_bind())
