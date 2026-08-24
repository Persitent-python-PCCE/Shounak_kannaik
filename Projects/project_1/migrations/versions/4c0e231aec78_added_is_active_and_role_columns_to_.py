from alembic import op
import sqlalchemy as sa


revision = '4c0e231aec78'
down_revision = '952840fe0553'
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('role', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('last_active', sa.DateTime(timezone=True), nullable=True))


def downgrade():

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('last_active')
        batch_op.drop_column('role')
        batch_op.drop_column('is_active')
