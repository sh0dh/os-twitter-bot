import os
from pathlib import Path

from dotenv import load_dotenv

from scripts.base import _call

ROOT_DIRECTORY = Path(__file__).parents[1]


def run() -> None:
    load_dotenv(ROOT_DIRECTORY / ".env")
    _call(f"uvicorn --reload src.healthz:app --port {os.getenv('PORT')}")
