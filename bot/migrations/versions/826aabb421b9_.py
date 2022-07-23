"""empty message

Revision ID: 826aabb421b9
Revises: ce56b612dad5
Create Date: 2022-07-23 15:02:35.915137

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '826aabb421b9'
down_revision = 'ce56b612dad5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('subscription_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subscription_type', sa.String(length=80), nullable=True),
    sa.Column('usd_price', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('one_time_subscription',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subscription_type_id', sa.Integer(), nullable=True),
    sa.Column('subscription_id', sa.Integer(), nullable=True),
    sa.Column('start_date', sa.DateTime(), nullable=True),
    sa.Column('end_date', sa.String(length=4), nullable=True),
    sa.ForeignKeyConstraint(['subscription_id'], ['subscription.id'], ),
    sa.ForeignKeyConstraint(['subscription_type_id'], ['subscription_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('weekly_subscription',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subscription_type_id', sa.Integer(), nullable=True),
    sa.Column('subscription_id', sa.Integer(), nullable=True),
    sa.Column('number_of_weeks', sa.Integer(), nullable=True),
    sa.Column('start_date', sa.DateTime(), nullable=True),
    sa.Column('end_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['subscription_id'], ['subscription.id'], ),
    sa.ForeignKeyConstraint(['subscription_type_id'], ['subscription_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('subscription', sa.Column('subscription_type_id', sa.Integer(), nullable=True))
    op.add_column('subscription', sa.Column('payment_chain_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'subscription', 'supported_chain', ['payment_chain_id'], ['id'])
    op.create_foreign_key(None, 'subscription', 'subscription_type', ['subscription_type_id'], ['id'])
    op.drop_column('subscription', 'start_date')
    op.drop_column('subscription', 'end_date')
    op.drop_column('subscription', 'subscription_status')
    op.drop_column('subscription', 'subscription_type')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('subscription', sa.Column('subscription_type', sa.VARCHAR(length=80), autoincrement=False, nullable=True))
    op.add_column('subscription', sa.Column('subscription_status', sa.VARCHAR(length=80), autoincrement=False, nullable=True))
    op.add_column('subscription', sa.Column('end_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('subscription', sa.Column('start_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'subscription', type_='foreignkey')
    op.drop_constraint(None, 'subscription', type_='foreignkey')
    op.drop_column('subscription', 'payment_chain_id')
    op.drop_column('subscription', 'subscription_type_id')
    op.drop_table('weekly_subscription')
    op.drop_table('one_time_subscription')
    op.drop_table('subscription_type')
    # ### end Alembic commands ###
