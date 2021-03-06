"""Migration 8

Revision ID: 1ef1adac3457
Revises: c1e545c147e6
Create Date: 2021-08-27 17:08:41.050728

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1ef1adac3457'
down_revision = 'c1e545c147e6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('electionparticipants', sa.Column('pollNumber', sa.Integer(), nullable=False))
    op.drop_column('electionparticipants', 'poolNumber')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('electionparticipants', sa.Column('poolNumber', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.drop_column('electionparticipants', 'pollNumber')
    # ### end Alembic commands ###
