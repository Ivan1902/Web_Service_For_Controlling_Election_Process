"""Migration 5

Revision ID: 573e05543dc9
Revises: 1e16f53d887e
Create Date: 2021-08-27 17:03:16.002059

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '573e05543dc9'
down_revision = '1e16f53d887e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('votes', sa.Column('ballotGuid', sa.String(length=256), nullable=False))
    op.drop_index('guid', table_name='votes')
    op.create_unique_constraint(None, 'votes', ['ballotGuid'])
    op.drop_column('votes', 'guid')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('votes', sa.Column('guid', mysql.VARCHAR(length=256), nullable=False))
    op.drop_constraint(None, 'votes', type_='unique')
    op.create_index('guid', 'votes', ['guid'], unique=False)
    op.drop_column('votes', 'ballotGuid')
    # ### end Alembic commands ###