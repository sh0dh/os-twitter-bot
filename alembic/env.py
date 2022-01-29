import os
from datetime import datetime, timezone
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import create_engine

from alembic import context
from config.console import logger

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    db_path = Path(__file__).parents[1]
    db_path.mkdir(parents=True, exist_ok=True)
    url = config.get_main_option(str(db_path / os.getenv("SQLITE_URL")))
    context.configure(
        url=f"sqlite:///{url}",
        target_metadata=None,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    db_path = Path(__file__).parents[1]
    db_path.mkdir(parents=True, exist_ok=True)
    db_url = str(db_path / os.getenv("SQLITE_URL"))
    connectable = create_engine(url=f"sqlite:///{db_url}")

    with connectable.connect() as connection:
        context.configure(connection=connection)

        with context.begin_transaction():
            ts_start = datetime.utcnow()
            logger.log(f"[ENV: {os.getenv('ENVIRONMENT')}] -> Starting migrations...")
            context.run_migrations()
            ts_end = datetime.utcnow()
            logger.log(f"[ENV: {os.getenv('ENVIRONMENT')}] -> Migration took: {ts_end - ts_start} secs")


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
