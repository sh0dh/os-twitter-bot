"""Add new tweeted_at column

Revision ID: 614217d47fd5
Revises: 25a55249b373
Create Date: 2021-10-03 11:37:03.621696

"""
import sqlalchemy as sa
from sqlalchemy.sql.functions import func

from alembic import op

# revision identifiers, used by Alembic.
revision = "614217d47fd5"
down_revision = "25a55249b373"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("sales", sa.Column("is_tweeted", sa.Boolean, default=True))
    op.add_column("sales", sa.Column("tweeted_at", sa.DateTime, nullable=True))
    op.create_index("sales_tweet_at_idx", "sales", ["is_tweeted"])


def downgrade():
    op.drop_index("sales_tweet_at_idx", table_name="sales")
    op.drop_column("sales", "tweeted_at")
    op.drop_column("sales", "is_tweeted")
