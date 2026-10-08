from sqlalchemy import create_engine, inspect, text

from app.database.migrations import upgrade_legacy_columns


def test_legacy_sqlite_database_receives_role_and_source_columns():
    engine = create_engine("sqlite:///:memory:")
    try:
        with engine.begin() as connection:
            connection.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, username VARCHAR(100))"))
            connection.execute(
                text("CREATE TABLE research_sources (id INTEGER PRIMARY KEY, title VARCHAR(255))")
            )

        upgrade_legacy_columns(engine)

        user_columns = {column["name"]: column for column in inspect(engine).get_columns("users")}
        source_columns = {column["name"] for column in inspect(engine).get_columns("research_sources")}
        assert user_columns["is_admin"]["default"] in ("FALSE", "false", "0")
        assert "source_type" in source_columns
    finally:
        engine.dispose()
