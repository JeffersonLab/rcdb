"""Conditions.time => time_value. SQL schema versioning incorporated

Revision ID: 34ba183eda63
Revises: None
Create Date: 2016-03-10 15:56:36.207352

"""

# revision identifiers, used by Alembic.
revision = '34ba183eda63'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from rcdb.model import SchemaVersion


def upgrade():
    op.create_table('schema_versions',
                    sa.Column('version', sa.Integer(), autoincrement=False, nullable=False),
                    sa.Column('created', sa.DateTime(), server_default='now()', nullable=True),
                    sa.Column('comment', sa.String(length=255), nullable=True),
                    sa.PrimaryKeyConstraint('version')
                    )
    op.drop_column(u'condition_types', 'is_many_per_run')
    op.add_column(u'conditions', sa.Column('time_value', sa.DateTime(), nullable=True))
    op.drop_column(u'conditions', 'time')
    op.alter_column(u'files', 'content',
                    existing_type=mysql.LONGTEXT(),
                    nullable=False)
    op.bulk_insert(SchemaVersion.__table__,
                   [
                       {'version': 1,
                        'comment': 'Conditions.time => time_value. SQL schema version added'}
                   ])


def downgrade():
    op.alter_column(u'files', 'content',
                    existing_type=mysql.LONGTEXT(),
                    nullable=True)
    op.add_column(u'conditions', sa.Column('time', mysql.DATETIME(), nullable=True))
    op.drop_column(u'conditions', 'time_value')
    op.add_column(u'condition_types', sa.Column('is_many_per_run', mysql.TINYINT(display_width=1), nullable=False))
    op.drop_table('schema_versions')

