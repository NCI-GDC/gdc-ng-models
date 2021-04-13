"""change columns to BigInteger

Revision ID: 12dbbcac7a1d
Revises: e9d53a640d5d
Create Date: 2021-03-30 13:16:01.055456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "12dbbcac7a1d"
down_revision = "e9d53a640d5d"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("notifications", "id", type_=sa.BigInteger)
    op.alter_column("qc_test_runs", "id", type_=sa.BigInteger)
    op.alter_column("qc_validation_results", "id", type_=sa.BigInteger)
    op.alter_column("qc_validation_results", "test_run_id", type_=sa.BigInteger)
    op.alter_column("redaction_log", "id", type_=sa.BigInteger)
    op.alter_column("redaction_entry", "redaction_id", type_=sa.BigInteger)
    op.alter_column("released_data_log", "id", type_=sa.BigInteger)
    op.alter_column("gdc_reports", "id", type_=sa.BigInteger)
    op.alter_column("study_rule", "id", type_=sa.BigInteger)
    op.alter_column("study_rule_program", "study_rule_id", type_=sa.BigInteger)
    op.alter_column("study_rule_program_project", "study_rule_id", type_=sa.BigInteger)
    op.alter_column("transaction_logs", "id", type_=sa.BigInteger)
    op.alter_column("transaction_snapshots", "transaction_id", type_=sa.BigInteger)
    op.alter_column("transaction_documents", "id", type_=sa.BigInteger)
    op.alter_column("transaction_documents", "transaction_id", type_=sa.BigInteger)


def downgrade():
    op.alter_column("notifications", "id", type_=sa.Integer)
    op.alter_column("qc_test_runs", "id", type_=sa.Integer)
    op.alter_column("qc_validation_results", "id", type_=sa.Integer)
    op.alter_column("qc_validation_results", "test_run_id", type_=sa.Integer)
    op.alter_column("redaction_log", "id", type_=sa.Integer)
    op.alter_column("redaction_entry", "redaction_id", type_=sa.Integer)
    op.alter_column("released_data_log", "id", type_=sa.Integer)
    op.alter_column("gdc_reports", "id", type_=sa.Integer)
    op.alter_column("study_rule", "id", type_=sa.Integer)
    op.alter_column("study_rule_program", "study_rule_id", type_=sa.Integer)
    op.alter_column("study_rule_program_project", "study_rule_id", type_=sa.Integer)
    op.alter_column("transaction_logs", "id", type_=sa.Integer)
    op.alter_column("transaction_snapshots", "transaction_id", type_=sa.Integer)
    op.alter_column("transaction_documents", "id", type_=sa.Integer)
    op.alter_column("transaction_documents", "transaction_id", type_=sa.Integer)
