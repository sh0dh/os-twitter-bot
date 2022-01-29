import os

import click
import dotenv

from alembic import command
from alembic.config import Config
from config.console import logger
from scripts.base import PROJECT_ROOT

alembic_cfg = Config((PROJECT_ROOT / "alembic.ini").as_posix())
dotenv.load_dotenv(PROJECT_ROOT / ".env")


def migrate() -> None:
    command.upgrade(alembic_cfg, "head")


def migration_history() -> None:
    command.history(alembic_cfg)


def legacy_db_stamp() -> None:
    command.stamp(alembic_cfg, "head")


@click.command()
@click.option("--version", type=str)
def rollback(version: str) -> None:
    logger.log("> DB:Run rollback...")
    command.downgrade(alembic_cfg, version)


def seed() -> None:
    logger.log("> DB:Seed database...")


@click.command()
@click.option("--commit_msg", type=str)
@click.option("--depends_on", type=str, default=None)
def generate_migration(commit_msg: str, depends_on: str) -> None:
    logger.log("> DB:Generate new migration")
    logger.log(f"  * Migration: {commit_msg} and depends on: {depends_on}")
    command.revision(alembic_cfg, message=commit_msg, autogenerate=False, depends_on=depends_on)
