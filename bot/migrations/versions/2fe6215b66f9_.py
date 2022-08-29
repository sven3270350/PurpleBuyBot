"""empty message

Revision ID: 2fe6215b66f9
Revises: 83849e5f1054
Create Date: 2022-08-29 22:33:38.465503

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2fe6215b66f9'
down_revision = '83849e5f1054'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('group', sa.Column('buy_icon', sa.String(length=2), nullable=True))
    op.add_column('group', sa.Column('buy_media', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('group', 'buy_media')
    op.drop_column('group', 'buy_icon')
    # ### end Alembic commands ###
