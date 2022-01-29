from datetime import datetime, timedelta
from pathlib import Path

import click
from dateutil.parser import parse
from dotenv import load_dotenv
from tweepy.error import TweepError

from config.console import logger
from src.models.model import ScheduledJobs
from src.utils.opensea import db_conn, parse_opensea_event
from src.utils.twitter_bot import tweet_backlog, tweet_sales, verify_twitter_app

ROOT_DIRECTORY = Path(__file__).parents[1]


@click.command()
@click.option("--collection", help="Put the collection name")
@click.option("--start_time", help="Add start time for backfill")
@click.option("--is_tweet", type=bool, default=False, help="Add start time for backfill")
def run_bot(collection: str, start_time: str, is_tweet: bool):
    load_dotenv(ROOT_DIRECTORY / ".env")
    logger.log(f"[green] Tweeting flag: {is_tweet}")
    if is_tweet:
        try:
            tweet_backlog()
            logger.log("Backlog of tweets done tweeting!")
        except TweepError as err:
            logger.log(f"[red] Tweep Error: {err.api_code}|{err.reason}")
    # ts_start = "2021-09-25 13:03:25"
    logger.log(f"[green] Starting twitter bot for collection:{collection} from {start_time}")
    parse_opensea_event(collection=collection, ts_before=start_time, mode="backfill", is_tweet=is_tweet)
    logger.log("[green] Tweets were successfully posted")
