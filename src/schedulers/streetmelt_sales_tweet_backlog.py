import time
import uuid
from datetime import datetime
from pathlib import Path

import schedule
from dateutil.parser import parse
from dotenv.main import load_dotenv
from sqlalchemy.sql.elements import and_

from config.console import logger
from src.models.model import ScheduledJobs
from src.utils.opensea import parse_opensea_event
from src.utils.twitter_bot import tweet_backlog
from src.utils.utilities import db_conn

FILE_DIRECTORY = Path(__file__).parents[2]
logger.log("Loading env file")
load_dotenv(FILE_DIRECTORY / ".env")


def run_twitter_bot_backlog_enqueue(**kwargs):
    ts_start = str(datetime.utcnow())
    with db_conn() as session:
        logger.log(f"[green] Starting vandul bot for @StreetMeltSales from {ts_start}")
        try:
            tweet_backlog()
            logger.log("[green] Tweets were successfully posted")
            job_to_do = ScheduledJobs(
                job_id=str(uuid.uuid4()),
                job_ts_start=parse(ts_start),
                project_slug="street-melts",
                is_successful=True,
                picked_at=parse(ts_start),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(job_to_do)
            session.commit()
        except Exception as err:
            logger.log(f"[red] Unsuccessful tweets: {err}")
            session.rollback()
            job_to_do = ScheduledJobs(
                job_id=str(uuid.uuid4()),
                job_ts_start=parse(ts_start),
                project_slug="street-melts",
                is_successful=False,
                picked_at=parse(ts_start),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(job_to_do)
            session.commit()


if __name__ == "__main__":
    logger.log(f"Adding tweet backlog jobs to queues every 15 minutes")
    schedule.every(15).minutes.do(run_twitter_bot_backlog_enqueue)
    while True:
        schedule.run_pending()
        time.sleep(900)
