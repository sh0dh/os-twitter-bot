import os
from datetime import datetime
from pathlib import Path
from typing import List

import tweepy
from dotenv import load_dotenv
from rich.progress import track
from tweepy.error import TweepError

from config.console import logger
from src.models.model import Sales
from src.utils.utilities import db_conn

ROOT_DIRECTORY = Path(__file__).parents[1]

load_dotenv(ROOT_DIRECTORY / ".env")


def verify_twitter_app():
    auth = tweepy.OAuthHandler(os.getenv("TWITTER_CONSUMER_KEY"), os.getenv("TWITTER_CONSUMER_SECRET"))
    auth.set_access_token(os.getenv("TWITTER_ACCESS_TOKEN"), os.getenv("TWITTER_ACCESS_TOKEN_SECRET"))

    api = tweepy.API(auth)
    return api


def tweet_format(event: dict):
    return f"💰{event['nft_name']} was sold to {event['purchaser']} (💵:{event['display_value']})\n🤑 Seller: {event['seller']}\n🤝Sold at: {str(event['sold_at'])} UTC\n{event['opensea_nft_link']}"


def tweet_sales_obj(event: Sales):
    return f"💰{event.nft_name} was sold to {event.purchaser} (💵:{event.display_value})\n🤑 Seller: {event.seller}\n🤝Sold at: {str(event.sold_at)} UTC\n{event.opensea_nft_link}"


def tweet_sales(api: tweepy.API, opensea_sales: List) -> None:
    for sale_event in track(opensea_sales):
        try:
            if type(sale_event) == Sales:
                api.update_status(tweet_sales_obj(event=sale_event))
                with db_conn() as session:
                    sale_event.is_tweeted = True
                    sale_event.tweeted_at = datetime.utcnow()
                    session.commit()
            else:
                api.update_status(tweet_format(event=sale_event))
                with db_conn() as session:
                    sale = session.query(Sales).filter(Sales.txn_id == sale_event["txn_id"]).first()
                    sale.is_tweeted = True
                    sale.tweeted_at = datetime.utcnow()
                    session.commit()
        except TweepError as err:
            logger.log(f"[red] Tweep Error: {err.api_code}|{err.reason}")
            if err.reason == "Status is a duplicate.":
                logger.log("[red] Duplicate tweets")
                continue


def tweet_backlog():
    with db_conn() as session:
        untweeted_sales = session.query(Sales).filter(Sales.is_tweeted == False).all()
        logger.log(f"Tweeting out {len(untweeted_sales)} backlogged tweets")
        tweet_sales(api=verify_twitter_app(), opensea_sales=untweeted_sales)
