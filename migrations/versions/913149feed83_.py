"""empty message

Revision ID: 913149feed83
Revises: 78aece093c53
Create Date: 2021-02-19 16:07:46.476210

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '913149feed83'
down_revision = '78aece093c53'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('image',
    sa.Column('filename', sa.String(length=128), nullable=False),
    sa.Column('data', sa.LargeBinary(), nullable=True),
    sa.PrimaryKeyConstraint('filename')
    )
    op.create_index(op.f('ix_image_filename'), 'image', ['filename'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_image_filename'), table_name='image')
    op.drop_table('image')
    # ### end Alembic commands ###
