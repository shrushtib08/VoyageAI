from pathlib import Path
import sys

from sqlalchemy import text

# Make "app" importable when this script is run from the project root.
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import engine


# GeoNames country codes used for the Asia dataset.
# Includes the major Asian countries and transcontinental countries
# relevant to an Asia-wide travel platform.
ASIA_COUNTRIES = {
    "AF",  # Afghanistan
    "AM",  # Armenia
    "AZ",  # Azerbaijan
    "BH",  # Bahrain
    "BD",  # Bangladesh
    "BT",  # Bhutan
    "BN",  # Brunei
    "KH",  # Cambodia
    "CN",  # China
    "CY",  # Cyprus
    "GE",  # Georgia
    "IN",  # India
    "ID",  # Indonesia
    "IR",  # Iran
    "IQ",  # Iraq
    "IL",  # Israel
    "JP",  # Japan
    "JO",  # Jordan
    "KZ",  # Kazakhstan
    "KW",  # Kuwait
    "KG",  # Kyrgyzstan
    "LA",  # Laos
    "LB",  # Lebanon
    "MY",  # Malaysia
    "MV",  # Maldives
    "MN",  # Mongolia
    "MM",  # Myanmar
    "NP",  # Nepal
    "KP",  # North Korea
    "OM",  # Oman
    "PK",  # Pakistan
    "PS",  # Palestine
    "PH",  # Philippines
    "QA",  # Qatar
    "SA",  # Saudi Arabia
    "SG",  # Singapore
    "KR",  # South Korea
    "LK",  # Sri Lanka
    "SY",  # Syria
    "TJ",  # Tajikistan
    "TH",  # Thailand
    "TL",  # Timor-Leste
    "TR",  # Turkey
    "TM",  # Turkmenistan
    "AE",  # United Arab Emirates
    "UZ",  # Uzbekistan
    "VN",  # Vietnam
    "YE",  # Yemen
    "TW",  # Taiwan
    "RU",  # Russia - included for Asia-wide travel coverage
}


SOURCE_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "Geonames"
    / "allCountries.txt"
)


BATCH_SIZE = 5000


def create_table():
    sql = """
    CREATE TABLE IF NOT EXISTS geographic_places (
        geoname_id BIGINT PRIMARY KEY,
        name TEXT NOT NULL,
        ascii_name TEXT,
        alternate_names TEXT,
        latitude DOUBLE PRECISION,
        longitude DOUBLE PRECISION,
        feature_class VARCHAR(1),
        feature_code VARCHAR(10),
        country_code VARCHAR(2),
        cc2 VARCHAR(200),
        admin1_code VARCHAR(20),
        admin2_code VARCHAR(80),
        admin3_code VARCHAR(20),
        admin4_code VARCHAR(20),
        population BIGINT,
        elevation INTEGER,
        dem INTEGER,
        timezone VARCHAR(64),
        modification_date DATE
    );
    """

    with engine.begin() as connection:
        connection.execute(text(sql))


def create_indexes():
    statements = [
        """
        CREATE INDEX IF NOT EXISTS idx_geographic_places_name
        ON geographic_places (name);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_geographic_places_country
        ON geographic_places (country_code);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_geographic_places_feature
        ON geographic_places (feature_class, feature_code);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_geographic_places_population
        ON geographic_places (population);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_geographic_places_coordinates
        ON geographic_places (latitude, longitude);
        """,
    ]
    index_operator_class = " text_pattern_ops" if engine.dialect.name == "postgresql" else ""
    statements.extend(
        [
            f"""
            CREATE INDEX IF NOT EXISTS idx_geographic_places_name_lower_prefix
            ON geographic_places (lower(name){index_operator_class});
            """,
            f"""
            CREATE INDEX IF NOT EXISTS idx_geographic_places_ascii_lower_prefix
            ON geographic_places (lower(ascii_name){index_operator_class});
            """,
        ]
    )

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def parse_int(value):
    if not value:
        return None

    try:
        return int(value)
    except ValueError:
        return None


def parse_float(value):
    if not value:
        return None

    try:
        return float(value)
    except ValueError:
        return None


def process_file():
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"GeoNames file not found:\n{SOURCE_FILE}"
        )

    print("=" * 70)
    print("VoyageAI Asia Geographic Database Importer")
    print("=" * 70)
    print(f"Source: {SOURCE_FILE}")
    print(f"File size: {SOURCE_FILE.stat().st_size / (1024 ** 3):.2f} GB")
    print(f"Asia country codes: {len(ASIA_COUNTRIES)}")
    print()

    insert_sql = text(
        """
        INSERT INTO geographic_places (
            geoname_id,
            name,
            ascii_name,
            alternate_names,
            latitude,
            longitude,
            feature_class,
            feature_code,
            country_code,
            cc2,
            admin1_code,
            admin2_code,
            admin3_code,
            admin4_code,
            population,
            elevation,
            dem,
            timezone,
            modification_date
        )
        VALUES (
            :geoname_id,
            :name,
            :ascii_name,
            :alternate_names,
            :latitude,
            :longitude,
            :feature_class,
            :feature_code,
            :country_code,
            :cc2,
            :admin1_code,
            :admin2_code,
            :admin3_code,
            :admin4_code,
            :population,
            :elevation,
            :dem,
            :timezone,
            :modification_date
        )
        ON CONFLICT (geoname_id)
        DO UPDATE SET
            name = EXCLUDED.name,
            ascii_name = EXCLUDED.ascii_name,
            alternate_names = EXCLUDED.alternate_names,
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude,
            feature_class = EXCLUDED.feature_class,
            feature_code = EXCLUDED.feature_code,
            country_code = EXCLUDED.country_code,
            cc2 = EXCLUDED.cc2,
            admin1_code = EXCLUDED.admin1_code,
            admin2_code = EXCLUDED.admin2_code,
            admin3_code = EXCLUDED.admin3_code,
            admin4_code = EXCLUDED.admin4_code,
            population = EXCLUDED.population,
            elevation = EXCLUDED.elevation,
            dem = EXCLUDED.dem,
            timezone = EXCLUDED.timezone,
            modification_date = EXCLUDED.modification_date
        """
    )

    total_read = 0
    total_asia = 0
    batch = []

    with engine.begin() as connection:
        with SOURCE_FILE.open(
            "r",
            encoding="utf-8",
            errors="replace",
            buffering=1024 * 1024,
        ) as file:

            for line in file:
                total_read += 1

                fields = line.rstrip("\n").split("\t")

                # GeoNames has 19 columns.
                if len(fields) != 19:
                    continue

                country_code = fields[8]

                # Keep the lookup dataset focused on inhabited places, not every
                # mountain, water feature, or administrative record in GeoNames.
                if country_code not in ASIA_COUNTRIES or fields[6] != "P":
                    continue
                population = parse_int(fields[14])
                if population is None or population <= 0:
                    continue

                batch.append(
                    {
                        "geoname_id": parse_int(fields[0]),
                        "name": fields[1],
                        "ascii_name": fields[2] or None,
                        "alternate_names": fields[3] or None,
                        "latitude": parse_float(fields[4]),
                        "longitude": parse_float(fields[5]),
                        "feature_class": fields[6] or None,
                        "feature_code": fields[7] or None,
                        "country_code": fields[8] or None,
                        "cc2": fields[9] or None,
                        "admin1_code": fields[10] or None,
                        "admin2_code": fields[11] or None,
                        "admin3_code": fields[12] or None,
                        "admin4_code": fields[13] or None,
                        "population": population,
                        "elevation": parse_int(fields[15]),
                        "dem": parse_int(fields[16]),
                        "timezone": fields[17] or None,
                        "modification_date": fields[18] or None,
                    }
                )

                total_asia += 1

                if len(batch) >= BATCH_SIZE:
                    connection.execute(insert_sql, batch)
                    batch.clear()

                    if total_asia % 50000 == 0:
                        print(
                            f"Processed: {total_read:,} lines | "
                            f"Asia records: {total_asia:,}"
                        )

        if batch:
            connection.execute(insert_sql, batch)

    print()
    print("Import completed.")
    print(f"Total GeoNames lines read: {total_read:,}")
    print(f"Asia records imported: {total_asia:,}")


def verify():
    with engine.connect() as connection:
        total = connection.execute(
            text("SELECT COUNT(*) FROM geographic_places")
        ).scalar()

        countries = connection.execute(
            text(
                """
                SELECT country_code, COUNT(*) AS place_count
                FROM geographic_places
                GROUP BY country_code
                ORDER BY country_code
                """
            )
        ).fetchall()

    print()
    print("=" * 70)
    print("DATABASE VERIFICATION")
    print("=" * 70)
    print(f"Total geographic records: {total:,}")
    print()

    for country_code, count in countries:
        print(f"{country_code}: {count:,}")


def main():
    create_table()
    process_file()
    create_indexes()
    verify()


if __name__ == "__main__":
    main()