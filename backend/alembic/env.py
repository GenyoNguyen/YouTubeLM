# Alembic environment configuration

from logging.config import fileConfig
from alembic import context

# Alembic config
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Your model's MetaData object here
target_metadata = None

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    pass

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    pass

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

