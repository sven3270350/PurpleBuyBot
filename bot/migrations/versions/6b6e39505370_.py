"""empty message

Revision ID: 6b6e39505370
Revises: 62637920f928
Create Date: 2022-09-08 00:46:11.460917

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b6e39505370'
down_revision = '62637920f928'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tracked_token', sa.Column('circulating_supply', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tracked_token', 'circulating_supply')
    # ### end Alembic commands ###