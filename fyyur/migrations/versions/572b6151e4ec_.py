"""empty message

Revision ID: 572b6151e4ec
Revises: 33c7e91170f2
Create Date: 2020-04-10 20:43:25.799060

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '572b6151e4ec'
down_revision = '33c7e91170f2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('shows',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['artists.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['venues.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('Shows')
    op.create_unique_constraint(None, 'venues', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'venues', type_='unique')
    op.create_table('Shows',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"Shows_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('start_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['artists.id'], name='Shows_artist_id_fkey'),
    sa.ForeignKeyConstraint(['venue_id'], ['venues.id'], name='Shows_venue_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='Shows_pkey')
    )
    op.drop_table('shows')
    # ### end Alembic commands ###
