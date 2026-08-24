from alembic import op
import sqlalchemy as sa


revision = '1698fa43aab2'
down_revision = '4c0e231aec78'
branch_labels = None
depends_on = None


def upgrade():

    op.create_table('booking_statuses',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('status_name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('status_name')
    )
    op.create_table('event_types',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('type_name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('type_name')
    )
    op.create_table('seats',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('section_id', sa.Integer(), nullable=False),
    sa.Column('row', sa.String(length=20), nullable=False),
    sa.Column('number', sa.String(length=20), nullable=False),
    sa.Column('seat_type', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sections',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('venues',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('address', sa.String(length=255), nullable=False),
    sa.Column('city', sa.String(length=255), nullable=False),
    sa.Column('state', sa.String(length=255), nullable=False),
    sa.Column('country', sa.String(length=255), nullable=False),
    sa.Column('capacity', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('booking_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('booking_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('seat_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(timezone=True), nullable=True))

    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('booking_reference', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('schedule_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('payment_mode_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('payment_status_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('booking_status_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('total_amount', sa.Numeric(precision=10, scale=2), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.create_unique_constraint(None, ['booking_reference'])

    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=255), nullable=False))
        batch_op.add_column(sa.Column('about', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('event_type_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('age_rating', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('poster_image_path', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))


def downgrade():

    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('poster_image_path')
        batch_op.drop_column('age_rating')
        batch_op.drop_column('event_type_id')
        batch_op.drop_column('about')
        batch_op.drop_column('name')

    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('total_amount')
        batch_op.drop_column('booking_status_id')
        batch_op.drop_column('payment_status_id')
        batch_op.drop_column('payment_mode_id')
        batch_op.drop_column('schedule_id')
        batch_op.drop_column('user_id')
        batch_op.drop_column('booking_reference')

    with op.batch_alter_table('booking_items', schema=None) as batch_op:
        batch_op.drop_column('created_at')
        batch_op.drop_column('price')
        batch_op.drop_column('seat_id')
        batch_op.drop_column('booking_id')

    op.drop_table('venues')
    op.drop_table('sections')
    op.drop_table('seats')
    op.drop_table('event_types')
    op.drop_table('booking_statuses')
