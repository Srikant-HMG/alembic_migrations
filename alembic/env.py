from logging.config import fileConfig
import sqlalchemy as sq
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy import create_engine
from alembic import context
import copy
import time
import json
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from core.DAL.Services.UserDAL.Models import DeclarativeBase as Base

target_metadata = Base.metadata
# target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def get_all_districts():
    district_schemas = ["a", "b", "c"]
    engine = create_engine("postgresql://postgres:password@localhost:5432/test2")
    print("it's called")
    for schama in district_schemas:
        if not engine.dialect.has_schema(engine, schama):
            engine.execute(sq.schema.CreateSchema(schama))

    return district_schemas

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    tables = target_metadata.tables
    tables = dict(tables)
    new_tables = dict()
    delete_schemas = []
    all_distict_schema_names = get_all_districts()
    # print("*****",tables)
    for i, j in tables.items():
        s = i.split(".")
        if len(s) > 1:
            if s[0] == "district_schema":
                # continue
                for name in all_distict_schema_names:
                    table_name_with_schema = name + "." + s[1]
                    new_tables[table_name_with_schema] = copy.deepcopy(tables[i])
                    new_tables[table_name_with_schema].schema = name
                delete_schemas.append(i)
        else:
            continue
            new_tables[i] = copy.deepcopy(tables[i])
    # while True:
    #     if len(delete_schemas) > 0:
    #         print("deleted once")
    #         print(delete_schemas)
    #         print(tables[delete_schemas[0]])
    #         del tables[delete_schemas[0]]
    #         del new_tables[delete_schemas[0]]
    #         del delete_schemas[0]
    #     else:
    #         break
    # tables.update(new_tables)
    print("***",new_tables)
    target_metadata.tables = new_tables
    print("***",new_tables)
    
    print("****",target_metadata.tables)

    with connectable.connect() as connection:

        def include_name(name, type_, parent_names):
            if type_ == "schema":
                # note this will not include the default schema
                return name in [None, "a", "b", "c"]
            else:
                return True
        
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # include_schemas=False,
            # include_name=include_name,
        )
        # context.configure.comparetype = True
        # context.configure.compare_server_default = True
        # context.configure.include_name = True
        with context.begin_transaction():
            context.run_migrations()
            


# if context.is_offline_mode():
#     run_migrations_offline()
# else:
#     
run_migrations_online()