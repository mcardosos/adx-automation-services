"""empty message

Revision ID: 9d5665354d34
Revises: 5e426c36c043
Create Date: 2018-01-20 17:38:42.457568

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d5665354d34'
down_revision = '5e426c36c043'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('task', 'log')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task', sa.Column('log', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
