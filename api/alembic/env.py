from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from app.config import settings
from app.models import Base

config = context.config
if config.config_file_name is not None and config.attributes.get("configure_logger", True):
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_online() -> None:
    url = config.get_main_option("sqlalchemy.url") or settings.database_url
    with create_engine(url).connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
