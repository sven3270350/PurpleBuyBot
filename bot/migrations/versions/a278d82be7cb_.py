"""empty message

Revision ID: a278d82be7cb
Revises: 2fe6215b66f9
Create Date: 2022-09-01 00:38:54.073521

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a278d82be7cb'
down_revision = '2fe6215b66f9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('subscription_payment_chain_id_fkey', 'subscription', type_='foreignkey')
    op.create_foreign_key(None, 'subscription', 'supported_chain', ['payment_chain_id'], ['chain_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'subscription', type_='foreignkey')
    op.create_foreign_key('subscription_payment_chain_id_fkey', 'subscription', 'supported_chain', ['payment_chain_id'], ['id'])
    # ### end Alembic commands ###
