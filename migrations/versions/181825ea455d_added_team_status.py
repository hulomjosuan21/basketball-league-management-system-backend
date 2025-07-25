"""added team status

Revision ID: 181825ea455d
Revises: e3731add0375
Create Date: 2025-06-30 07:35:55.000662

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '181825ea455d'
down_revision = 'e3731add0375'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('teams_table', schema=None) as batch_op:
        batch_op.add_column(sa.Column('team_category', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('teams_table', schema=None) as batch_op:
        batch_op.drop_column('team_category')

    # ### end Alembic commands ###
