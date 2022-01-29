import os
from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional

import requests
from dateutil import parser
from loguru import logger as log
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from requests import Request
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from tweepy.error import TweepError

from config.console import logger
from src.models.model import Sales
from src.utils.schemas import CryptoToken, VandulSaleDetail
from src.utils.twitter_bot import tweet_sales, verify_twitter_app
from src.utils.utilities import db_conn


def generate_datetimes(ts_start, ts_end, delta):
    current = ts_start
    while current < ts_end:
        yield current
        current += delta


def get_proxy_format(proxy_element: str):
    return f"http://{proxy_element['proxy_address']}:{proxy_element['ports']['http']}:{proxy_element['username']}:{proxy_element['password']}"


def fetch_proxies(debug: bool = False):
    logger.log("[green] Fetching proxies...")

    proxy_response = requests.get(
        os.getenv("PROXY_API_URL"),
        headers={"Authorization": f"Token {os.getenv('PROXY_API_KEY')}"},
        timeout=120,
    )
    proxies = []
    if proxy_response.status_code == 200:
        proxies = [get_proxy_format(proxy_element=elem) for elem in proxy_response.json()["results"]]
    else:
        logger.log("[red] Proxies couldn't be fetched")
    return proxies


def fetch_opensea_events(
    collection_slug: str,
    ts_before: datetime,
    ts_after: datetime,
    event_type: str = "successful",
    limit: str = 50,
) -> Dict:
    proxies = fetch_proxies(debug=True) # Ignore this if you don't have proxies: Make this -> proxies = []
    querystring = {
        "collection_slug": collection_slug,
        "only_opensea": "true",
        "offset": "0",
        "limit": limit,
        "occurred_before": ts_before,
        "occurred_after": ts_after,
        "event_type": event_type,
    }

    headers = {"Accept": "application/json", "X-API-KEY": os.getenv("OPENSEA_API_KEY")}
    logger.log(f"[yellow] Fetching events from opensea.io for project:{collection_slug}")
    response = requests.get(
        os.getenv("OPENSEA_EVENTS_API"), headers=headers, params=querystring, proxies={"http": proxies}, timeout=120
    )
    if response.status_code != 200:
        logger.log(
            f"Opensea request could not be honoured for project: {collection_slug}. Got status: {response.status_code}. Debug: {response.json()}"
        )
        return {"asset_events": []}
    logger.log(f"[green] Successfully fetched events from opensea.io for project:{collection_slug}")
    return response.json()


def get_backfilled_ts(ts_before: str):
    return [dt_ for dt_ in generate_datetimes(parser.parse(ts_before), datetime.utcnow(), timedelta(minutes=5))]


def cleanup_opensea_events(opensea_events: List, collection: str, ts_before: str, ts_after: str):
    sales = []
    for event in opensea_events:
        with db_conn() as session:
            try:
                token_details = {
                    "symbol": event["payment_token"]["symbol"],
                    "name": event["payment_token"]["symbol"],
                    "usd_value": event["payment_token"]["usd_price"],
                    "decimals": event["payment_token"]["decimals"],
                }
                opensea_purchaser = None
                opensea_purchaser_eth_addr = None
                if event["transaction"]["from_account"]:
                    if event["transaction"]["from_account"]["user"]:
                        opensea_purchaser = event["transaction"]["from_account"]["user"]["username"]
                        opensea_purchaser_eth_addr = event["transaction"]["from_account"]["address"]
                sold_at = event["transaction"]["timestamp"]
                txn_id = event["transaction"]["id"]
                eth_block_hash = event["transaction"]["block_hash"]
                eth_block_number = event["transaction"]["block_number"]
                discord_url = event["asset"]["collection"]["discord_url"]
                twitter_username = event["asset"]["collection"]["twitter_username"]
                instagrame_username = event["asset"]["collection"]["instagram_username"]
                collection_name = event["asset"]["collection"]["name"]
                opensea_link = event["asset"]["permalink"]
                opensea_seller = None
                if event["seller"]:
                    if event["seller"]["user"]:
                        opensea_seller = event["seller"]["user"]["username"]
                total_sales_for_nft = event["asset"]["num_sales"]
                nft_sale_value = int(event["total_price"]) / int(str(1).ljust(token_details["decimals"] + 1, "0"))
                display_value = f"{nft_sale_value} {token_details['name']}"
                nft_name = event["asset"]["name"]
                nft_url = event["asset"]["image_url"]

                is_txn_present = session.query(Sales).filter(Sales.txn_id == txn_id).first()
                if is_txn_present:
                    logger.log(f"[bold red] Event: {txn_id} has already been tweeted out!")
                    continue
                sale = Sales(
                    purchaser="Anon" if opensea_purchaser is None else opensea_purchaser,
                    seller="Anon" if opensea_seller is None else opensea_seller,
                    sold_at=parser.parse(sold_at),
                    txn_id=txn_id,
                    eth_block_hash=eth_block_hash,
                    eth_block_number=eth_block_number,
                    purchaser_addr=opensea_purchaser_eth_addr,
                    discord_url=discord_url,
                    twitter_handle=twitter_username,
                    instagram_handle=instagrame_username,
                    collection_name=collection_name,
                    opensea_nft_link=opensea_link,
                    token_details=token_details,
                    total_sales=total_sales_for_nft,
                    nft_name=nft_name,
                    nft_url=nft_url,
                    display_value=display_value,
                    is_tweeted=False,
                    tweeted_at=None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                session.add(sale)
                session.commit()
                sales_pyd = sqlalchemy_to_pydantic(Sales)
                sales.append(sales_pyd.from_orm(sale).dict())
            except Exception as err:
                logger.log(f"[red] Error: {err}")
                log.exception(err)
    logger.log(
        f"[teal] Found {len(opensea_events)} sales for collection: {collection} between {ts_after} and {ts_before}"
    )
    return sales


def parse_opensea_event(
    collection: str, ts_before: str = str(datetime.utcnow()), mode: str = "backfill", is_tweet: bool = False
) -> List[VandulSaleDetail]:
    timestamp_list = None
    sales_list = []
    if mode == "backfill":
        logger.log(f"[orange] Starting backfill from {ts_before}")
        timestamp_list = get_backfilled_ts(ts_before=ts_before)
        logger.log(f"[bold yellow] Timestamp list: {timestamp_list}")

    if not timestamp_list:
        ts_start = parser.parse(ts_before) - timedelta(minutes=10)
        logger.log(f"[orange] Fetching opensea events for collection: {collection} between {ts_start} and {ts_before}")
        opensea_events = fetch_opensea_events(
            collection_slug=collection, ts_before=parser.parse(ts_before), ts_after=ts_start
        )["asset_events"]
        if not opensea_events:
            logger.log(
                f"[teal] Found {len(opensea_events)} sales for collection: {collection} between {ts_start} and {str(ts_before)}"
            )
            return []
        sales_list = cleanup_opensea_events(
            opensea_events=opensea_events, collection=collection, ts_before=ts_start, ts_after=str(ts_before)
        )
    else:
        for idx, backfilled_timestamp in enumerate(timestamp_list):
            opensea_events = []
            if idx == (len(timestamp_list) - 1):
                continue
            ts_start = backfilled_timestamp
            ts_before = timestamp_list[idx + 1]
            logger.log(
                f"[orange] Fetching opensea events for collection: {collection} between {ts_start} and {ts_before}"
            )
            opensea_events = fetch_opensea_events(collection_slug=collection, ts_before=ts_before, ts_after=ts_start)[
                "asset_events"
            ]
            if not opensea_events:
                logger.log(
                    f"[teal] Found {len(opensea_events)} sales for collection: {collection} between {ts_start} and {str(ts_before)}"
                )
                continue
            sales_list = cleanup_opensea_events(
                opensea_events=opensea_events, collection=collection, ts_before=str(ts_before), ts_after=str(ts_start)
            )
            logger.log(f"Tweeting {len(sales_list)} sale events")
            try:
                tweet_api = verify_twitter_app()
                if not tweet_api:
                    logger.log(f"@EtherGalsSales app could not be verified...")
                tweet_sales(api=tweet_api, opensea_sales=sales_list)
            except TweepError as err:
                logger.log(f"[red] Tweep Error: {err.api_code}|{err.reason}")

    if is_tweet and not timestamp_list:
        logger.log(f"Tweeting {len(sales_list)} sale events")
        try:
            tweet_api = verify_twitter_app()
            if not tweet_api:
                logger.log(f"@EtherGalsSales app could not be verified...")
            tweet_sales(api=tweet_api, opensea_sales=sales_list)
        except TweepError as err:
            logger.log(f"[red] Tweep Error: {err.api_code}|{err.reason}")
    return True
