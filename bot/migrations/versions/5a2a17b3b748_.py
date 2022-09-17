"""empty message

Revision ID: 5a2a17b3b748
Revises: 6b6e39505370
Create Date: 2022-09-16 06:56:45.354967

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a2a17b3b748'
down_revision = '6b6e39505370'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('campaigns', sa.Column('interval', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('campaigns', 'interval')
    # ### end Alembic commands ###
