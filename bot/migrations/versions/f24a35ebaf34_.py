"""empty message

Revision ID: f24a35ebaf34
Revises: ffffc9461c26
Create Date: 2022-07-12 14:46:17.621987

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f24a35ebaf34'
down_revision = 'ffffc9461c26'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('supported_exchange',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('exchange_name', sa.String(length=20), nullable=True),
    sa.Column('router_address', sa.String(length=100), nullable=True),
    sa.Column('chain_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['chain_id'], ['supported_chain.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('supported_pairs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pair_name', sa.String(length=20), nullable=True),
    sa.Column('pair_address', sa.String(length=100), nullable=True),
    sa.Column('chain_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['chain_id'], ['supported_chain.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('supported_pairs')
    op.drop_table('supported_exchange')
    # ### end Alembic commands ###
