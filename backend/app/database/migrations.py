from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def upgrade_legacy_columns(engine: Engine) -> None:
    """Apply additive schema updates for databases created before these fields existed."""
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    changes = {
        "users": ("is_admin", "BOOLEAN NOT NULL DEFAULT FALSE"),
        "research_sources": ("source_type", "VARCHAR(50)"),
    }

    with engine.begin() as connection:
        for table, (column, definition) in changes.items():
            if table in tables:
                columns = {item["name"] for item in inspector.get_columns(table)}
                if column not in columns:
                    connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}"))
