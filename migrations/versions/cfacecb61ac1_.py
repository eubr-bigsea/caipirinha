"""empty message

Revision ID: cfacecb61ac1
Revises: ed3b7980089f
Create Date: 2017-08-29 16:04:04.529943

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = 'cfacecb61ac1'
down_revision = 'ed3b7980089f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    bind = op.get_bind()
    if bind.engine.name == 'mysql':
        op.add_column('dashboard',
                  sa.Column('configuration', mysql.LONGTEXT(), nullable=True))
    else:
        op.add_column('dashboard',
                  sa.Column('configuration', sa.Text(), nullable=True))

    op.add_column('dashboard',
                  sa.Column('is_public', sa.Boolean(),
                            default=True,
                            nullable=False))
    op.execute(text(
        "UPDATE visualization_type SET name = 'scatter-plot' WHERE id =87"
    ))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('dashboard', 'is_public')
    op.drop_column('dashboard', 'configuration')

    op.execute(text(
        "UPDATE visualization_type SET name = 'plot-chart' WHERE id =87"
    ))
    # ### end Alembic commands ###
