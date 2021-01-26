"""empty message

Revision ID: a1a123c09c09
Revises: ac734c4d602b
Create Date: 2021-01-23 00:50:07.935501

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1a123c09c09'
down_revision = 'ac734c4d602b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movie', sa.Column('timestamp', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('movie', 'timestamp')
    # ### end Alembic commands ###
