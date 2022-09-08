"""empty message

Revision ID: 62637920f928
Revises: efe976907dbb
Create Date: 2022-09-08 00:44:58.581121

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '62637920f928'
down_revision = 'efe976907dbb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tracked_token', 'circulating_supply')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tracked_token', sa.Column('circulating_supply', sa.BIGINT(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
