"""Create streemelt_jobs table

Revision ID: cd50e65c511b
Revises:
Create Date: 2021-09-25 11:41:23.169880

"""
import uuid
from datetime import datetime, timedelta
from typing import Optional

import sqlalchemy as sa
from dateutil.parser import parse
from pydantic import BaseModel
from rich.progress import track
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import MetaData, Table

from alembic import op
from config.console import logger
from src.utils.opensea import generate_datetimes

# revision identifiers, used by Alembic.
revision = "cd50e65c511b"
down_revision = None
branch_labels = None
depends_on = None


class ScheduledJobsPd(BaseModel):
    id: int
    job_id: str
    job_ts_start: datetime
    project_slug: str
    is_successful: bool
    picked_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


def upgrade():
    op.create_table(
        "scheduled_jobs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("job_id", sa.String(), nullable=False),
        sa.Column("job_ts_start", sa.DateTime, nullable=False),
        sa.Column("project_slug", sa.String(), nullable=False),
        sa.Column("is_successful", sa.Boolean, nullable=False),
        sa.Column("picked_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_onupdate=func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_onupdate=func.now()),
    )
    op.create_index("scheduled_jobs_id_idx", "scheduled_jobs", ["job_id"], unique=True)
    op.create_index("scheduled_jobs_ts_start_idx", "scheduled_jobs", ["job_ts_start"], unique=True)
    op.create_index("scheduled_jobs_picked_at_idx", "scheduled_jobs", ["picked_at"])
    op.create_index("scheduled_jobs_is_success_idx", "scheduled_jobs", ["is_successful"])
    op.create_index("scheduled_jobs_composite_one_idx", "scheduled_jobs", ["job_id", "is_successful"])


def downgrade():
    indexes = [
        "scheduled_jobs_id_idx",
        "scheduled_jobs_ts_start_idx",
        "scheduled_jobs_picked_at_idx",
        "scheduled_jobs_is_success_idx",
        "scheduled_jobs_composite_one_idx",
    ]
    for idx in indexes:
        op.drop_index(idx, table_name="scheduled_jobs")
    op.drop_table("scheduled_jobs")
