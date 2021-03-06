"""empty message

Revision ID: a8b560d08c5e
Revises: 58ccb31a84cd
Create Date: 2021-02-13 01:00:50.581821

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a8b560d08c5e'
down_revision = '58ccb31a84cd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movie', sa.Column('director_id', sa.Integer(), nullable=True))
    op.add_column('movie', sa.Column('trailer_url', sa.String(length=128), nullable=True))
    op.create_unique_constraint(None, 'movie', ['trailer_url'])
    op.create_foreign_key(None, 'movie', 'actor', ['director_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'movie', type_='foreignkey')
    op.drop_constraint(None, 'movie', type_='unique')
    op.drop_column('movie', 'trailer_url')
    op.drop_column('movie', 'director_id')
    # ### end Alembic commands ###
