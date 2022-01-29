from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CryptoToken(BaseModel):
    symbol: str
    name: str
    usd_value: str
    decimals: int


class VandulSaleDetail(BaseModel):
    purchaser: Optional[str]
    seller: Optional[str]
    sold_at: datetime
    txn_id: str
    eth_block_hash: str
    eth_block_number: str
    purchaser_addr: Optional[str]
    discord_url: Optional[str]
    twitter_handle: Optional[str]
    instagram_handle: Optional[str]
    collection_name: str
    opensea_nft_link: str
    token_details: dict
    total_sales: int
    nft_name: str
    nft_url: str
    display_value: str
    created_at: datetime
    updated_at: datetime
