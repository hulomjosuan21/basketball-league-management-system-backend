"""asdds

Revision ID: aaf0dc9afa86
Revises: a04a1f3a2193
Create Date: 2025-07-20 21:10:30.054994

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'aaf0dc9afa86'
down_revision = 'a04a1f3a2193'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('matches_table', schema=None) as batch_op:
        batch_op.alter_column('scheduled_date',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True)
        batch_op.alter_column('court',
               existing_type=sa.VARCHAR(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('matches_table', schema=None) as batch_op:
        batch_op.alter_column('court',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.alter_column('scheduled_date',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False)

    # ### end Alembic commands ###
