"""added constraints

Revision ID: dfeaef489a54
Revises: 15d459b77fd1
Create Date: 2025-07-22 20:02:45.665225

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dfeaef489a54'
down_revision = '15d459b77fd1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('matches_table', schema=None) as batch_op:
        batch_op.create_unique_constraint('unique_match_per_category_and_division', ['league_id', 'category', 'division_id', 'round_number', 'home_team_id', 'away_team_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('matches_table', schema=None) as batch_op:
        batch_op.drop_constraint('unique_match_per_category_and_division', type_='unique')

    # ### end Alembic commands ###
