"""Add diff of height and distance

Revision ID: d8e74548efa1
Revises: c7dd6d36b41e
Create Date: 2022-11-02 16:39:00.667650

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd8e74548efa1'
down_revision = 'c7dd6d36b41e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('gpsreadings', sa.Column('distance_to_prev', sa.Float(), nullable=True))
    op.add_column('gpsreadings', sa.Column('height_to_prev', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('gpsreadings', 'height_to_prev')
    op.drop_column('gpsreadings', 'distance_to_prev')
    # ### end Alembic commands ###