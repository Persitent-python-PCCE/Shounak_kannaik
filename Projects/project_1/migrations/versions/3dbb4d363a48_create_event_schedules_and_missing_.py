from alembic import op
import sqlalchemy as sa


revision = '3dbb4d363a48'
down_revision = '1698fa43aab2'
branch_labels = None
depends_on = None


def upgrade():

    op.create_table('genres',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('genre_name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('genre_name')
    )
    op.create_table('payment_modes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('mode_name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('mode_name')
    )
    op.create_table('payment_statuses',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('status_name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('status_name')
    )
    op.create_table('user_documents',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('doc_type', sa.String(length=50), nullable=False),
    sa.Column('file_path', sa.String(length=255), nullable=False),
    sa.Column('verified', sa.Boolean(), nullable=True),
    sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('event_genres',
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['genre_id'], ['genres.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('event_id', 'genre_id')
    )
    op.create_table('event_schedules',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('start_datetime', sa.DateTime(timezone=True), nullable=False),
    sa.Column('end_datetime', sa.DateTime(timezone=True), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['venue_id'], ['venues.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payment_transactions',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('booking_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('gateway_transaction_id', sa.String(length=100), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('booking_items', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'seats', ['seat_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key(None, 'bookings', ['booking_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'event_schedules', ['schedule_id'], ['id'])
        batch_op.create_foreign_key(None, 'booking_statuses', ['booking_status_id'], ['id'])
        batch_op.create_foreign_key(None, 'users', ['user_id'], ['id'])
        batch_op.create_foreign_key(None, 'payment_statuses', ['payment_status_id'], ['id'])
        batch_op.create_foreign_key(None, 'payment_modes', ['payment_mode_id'], ['id'])

    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'event_types', ['event_type_id'], ['id'], ondelete='SET NULL')

    with op.batch_alter_table('seats', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'sections', ['section_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('sections', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'venues', ['venue_id'], ['id'], ondelete='CASCADE')


def downgrade():

    with op.batch_alter_table('sections', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('seats', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('booking_items', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')

    op.drop_table('payment_transactions')
    op.drop_table('event_schedules')
    op.drop_table('event_genres')
    op.drop_table('user_documents')
    op.drop_table('payment_statuses')
    op.drop_table('payment_modes')
    op.drop_table('genres')
