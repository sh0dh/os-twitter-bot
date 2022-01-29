from sqlalchemy import JSON, TIMESTAMP, Column, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Table
from sqlalchemy.sql.sqltypes import VARCHAR, Boolean, DateTime, Integer, Text

Base = declarative_base()
metadata = Base.metadata

scheduled_jobs_table = Table(
    "scheduled_jobs",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("job_id", Text),
    Column("job_ts_start", DateTime(timezone=True)),
    Column("project_slug", Text),
    Column("is_successful", Boolean),
    Column("picked_at", DateTime(timezone=True)),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), server_default=func.now()),
)


class ScheduledJobs(Base):

    __table__ = scheduled_jobs_table


sales_table = Table(
    "sales",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("purchaser", Text, nullable=True),
    Column("seller", Text, nullable=True),
    Column("sold_at", DateTime, nullable=False),
    Column("txn_id", Text, nullable=False),
    Column("eth_block_hash", Text, nullable=False),
    Column("eth_block_number", Text, nullable=False),
    Column("purchaser_addr", Text, nullable=True),
    Column("discord_url", Text, nullable=True),
    Column("twitter_handle", Text, nullable=True),
    Column("instagram_handle", Text, nullable=True),
    Column("collection_name", Text, nullable=False),
    Column("opensea_nft_link", Text, nullable=False),
    Column("token_details", JSON, nullable=False),
    Column("total_sales", Integer, nullable=False),
    Column("nft_name", Text, nullable=False),
    Column("nft_url", Text, nullable=False),
    Column("display_value", Text, nullable=False),
    Column("is_tweeted", Boolean, nullable=False),
    Column("tweeted_at", DateTime(timezone=True), server_default=func.now()),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), server_default=func.now()),
)


class Sales(Base):

    __table__ = sales_table
