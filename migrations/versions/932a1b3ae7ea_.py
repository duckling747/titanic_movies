"""empty message

Revision ID: 932a1b3ae7ea
Revises: f0dbfce9752a
Create Date: 2021-02-10 01:25:09.170262

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '932a1b3ae7ea'
down_revision = 'f0dbfce9752a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movie', sa.Column('synopsis', sa.String(length=256), nullable=True))
    op.create_unique_constraint(None, 'movie', ['synopsis'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'movie', type_='unique')
    op.drop_column('movie', 'synopsis')
    # ### end Alembic commands ###
