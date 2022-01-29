"""Create sales table

Revision ID: 25a55249b373
Revises: cd50e65c511b
Create Date: 2021-09-25 12:53:42.967976

"""
import sqlalchemy as sa
from sqlalchemy.sql.functions import func

from alembic import op

# revision identifiers, used by Alembic.
revision = "25a55249b373"
down_revision = "cd50e65c511b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "sales",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("purchaser", sa.String, nullable=True),
        sa.Column("seller", sa.String, nullable=True),
        sa.Column("sold_at", sa.DateTime, nullable=False),
        sa.Column("txn_id", sa.String, nullable=False),
        sa.Column("eth_block_hash", sa.String, nullable=False),
        sa.Column("eth_block_number", sa.String, nullable=False),
        sa.Column("purchaser_addr", sa.String, nullable=True),
        sa.Column("discord_url", sa.String, nullable=True),
        sa.Column("twitter_handle", sa.String, nullable=True),
        sa.Column("instagram_handle", sa.String, nullable=True),
        sa.Column("collection_name", sa.String, nullable=False),
        sa.Column("opensea_nft_link", sa.String, nullable=False),
        sa.Column("token_details", sa.JSON, nullable=True),
        sa.Column("total_sales", sa.Integer, nullable=False),
        sa.Column("nft_name", sa.String, nullable=False),
        sa.Column("nft_url", sa.String, nullable=False),
        sa.Column("display_value", sa.String, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_onupdate=func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_onupdate=func.now()),
    )
    op.create_index("sales_txn_id_idx", "sales", ["txn_id"], unique=True)
    op.create_index("sales_seller_idx", "sales", ["seller"])
    op.create_index("sales_display_value_idx", "sales", ["display_value"])
    op.create_index("sales_purchaser_idx", "sales", ["purchaser"])


def downgrade():
    indexes = [
        "sales_txn_id_idx",
        "sales_seller_idx",
        "sales_display_value_idx",
        "sales_purchaser_idx",
    ]
    for idx in indexes:
        op.drop_index(idx, "sales")
    op.drop_table("sales")
