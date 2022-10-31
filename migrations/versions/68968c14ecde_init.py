"""init

Revision ID: 68968c14ecde
Revises: 
Create Date: 2022-10-31 18:08:07.274321

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '68968c14ecde'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blesensors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('address', sa.String(length=100), nullable=False),
    sa.Column('sensor_type', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('address')
    )
    op.create_table('rides',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.Column('end_time', sa.DateTime(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('enviroreadings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('ride_id', sa.Integer(), nullable=True),
    sa.Column('temp', sa.Float(), nullable=True),
    sa.Column('altitude', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['ride_id'], ['rides.id'], name='fk_enviroreadings_rides_id_ride_id', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('gpsreadings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('ride_id', sa.Integer(), nullable=True),
    sa.Column('latitude', sa.Float(), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=True),
    sa.Column('altitude', sa.Float(), nullable=True),
    sa.Column('speed', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['ride_id'], ['rides.id'], name='fk_gpsreadings_rides_id_ride_id', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('hrreadings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('ride_id', sa.Integer(), nullable=True),
    sa.Column('bpm', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['ride_id'], ['rides.id'], name='fk_hrreadings_rides_id_ride_id', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('powerreadings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('ride_id', sa.Integer(), nullable=True),
    sa.Column('power', sa.Integer(), nullable=True),
    sa.Column('cadence', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['ride_id'], ['rides.id'], name='fk_powerreadings_rides_id_ride_id', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('powerreadings')
    op.drop_table('hrreadings')
    op.drop_table('gpsreadings')
    op.drop_table('enviroreadings')
    op.drop_table('rides')
    op.drop_table('blesensors')
    # ### end Alembic commands ###