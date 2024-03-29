""" Plotly

Revision ID: edcfd0652442
Revises: 437ffc36a821
Create Date: 2023-03-24 15:57:58.156986

"""
from alembic import op
from sqlalchemy import String, Integer
from sqlalchemy.sql import table, column, text
from caipirinha.migration_utils import get_enable_disable_fk_command
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'edcfd0652442'
down_revision = '437ffc36a821'
branch_labels = None
depends_on = None


def insert_visualization_type():
    tb = table(
        'visualization_type',
        column('id', Integer),
        column('name', String),
        column('help', String),
        column('icon', String))

    all_ops = [
        (145, 'plotly', 'Plotly', 'fa-chart'),
    ]
    rows = [dict(zip([c.name for c in tb.columns], operation)) for operation in
            all_ops]

    op.bulk_insert(tb, rows)


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    try:
        op.execute(text('BEGIN'))
        insert_visualization_type()
        op.execute(text('COMMIT'))
    except:
        op.execute(text('ROLLBACK'))
        raise


# noinspection PyBroadException
def downgrade():
    try:
        op.execute(text('BEGIN'))
        op.execute(text(get_enable_disable_fk_command(False)))
        op.execute(
            text("DELETE FROM visualization_type WHERE id IN (145)"))
        op.execute(text(get_enable_disable_fk_command(True)))
        op.execute(text('COMMIT'))
    except:
        op.execute(text('ROLLBACK'))
        raise
