from alembic import op
import sqlalchemy as sa


revision = '16a8ebfa074c'
down_revision = '3dbb4d363a48'
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table('sections', schema=None) as batch_op:
        batch_op.add_column(sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False))


def downgrade():

    with op.batch_alter_table('sections', schema=None) as batch_op:
        batch_op.drop_column('price')
