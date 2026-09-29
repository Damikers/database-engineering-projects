import sys
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import sessionmaker

from config import BASE_DIR, DATABASE_URL, CSV_PATH
from models.weather import Base, Weather, WindDirection
from models.air_quality import AirQuality
from layers.repository import WeatherRepository
from layers.service import WeatherService
from layers.cli import WeatherCLI

engine  = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

DIRECTION_MAP = {d.value: d for d in WindDirection}


def safe_direction(val):
    if pd.isna(val):
        return None
    return DIRECTION_MAP.get(str(val).strip().upper(), None)


def safe_time(val):
    if pd.isna(val):
        return None
    for fmt in ("%I:%M %p", "%H:%M"):
        try:
            return datetime.strptime(str(val).strip(), fmt).time()
        except ValueError:
            continue
    return None


def safe_float(val):
    try:
        return float(val) if pd.notna(val) else None
    except (ValueError, TypeError):
        return None


def safe_int(val):
    try:
        return int(val) if pd.notna(val) else None
    except (ValueError, TypeError):
        return None


def alembic_upgrade_head():
    from alembic import command
    from alembic.config import Config

    cfg = Config(str(BASE_DIR / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    command.upgrade(cfg, "head")


def ensure_schema_or_die():
    insp = inspect(engine)
    if not insp.has_table("weather") or not insp.has_table("air_quality"):
        raise RuntimeError(
            "Таблиці не знайдено. Спочатку виконайте `python main.py init` "
            "(або `alembic upgrade head`)."
        )
    aq_cols = {c["name"] for c in insp.get_columns("air_quality")}
    if "go_outside" not in aq_cols:
        raise RuntimeError(
            "Колонку `air_quality.go_outside` не знайдено. "
            "Оновіть міграції: `python main.py init` (або `alembic upgrade head`)."
        )


def load_csv_to_db(csv_path: str = CSV_PATH, limit: int = None):
    ensure_schema_or_die()
    print(f"Читаємо {csv_path}...")
    df = pd.read_csv(csv_path)
    if limit:
        df = df.head(limit)
    print(f"Рядків для завантаження: {len(df)}")

    df["last_updated"] = pd.to_datetime(
        df["last_updated"], errors="coerce"
    ).dt.date
    df = df[df["last_updated"].notna()]

    session = Session()
    repo    = WeatherRepository(session)
    service = WeatherService(repo)

    weather_records = []
    for _, row in df.iterrows():
        country = str(row.get("country", "")).strip()
        if not country:
            continue
        weather_records.append({
            "country":      country,
            "last_updated": row["last_updated"],
            "sunrise":      safe_time(row.get("sunrise")),
            "wind_kph":     safe_float(row.get("wind_kph")),
            "wind_degree":  safe_int(row.get("wind_degree")),
            "wind_dir":     safe_direction(row.get("wind_dir")),
        })

    repo.bulk_insert_weather(weather_records)
    print(f"Weather: {len(weather_records)} рядків вставлено")

    id_rows = session.execute(
        select(Weather.id, Weather.country, Weather.last_updated)
    ).all()
    id_map = {(c, d): i for i, c, d in id_rows}

    aq_records = []
    for _, row in df.iterrows():
        key        = (str(row.get("country", "")).strip(), row["last_updated"])
        weather_id = id_map.get(key)
        if not weather_id:
            continue

        epa   = safe_int(row.get("air_quality_us-epa-index"))
        pm25  = safe_float(row.get("air_quality_PM2.5"))
        ozone = safe_float(row.get("air_quality_Ozone"))

        aq_records.append({
            "weather_id":      weather_id,
            "air_co":          safe_float(row.get("air_quality_Carbon_Monoxide")),
            "air_no2":         safe_float(row.get("air_quality_Nitrogen_dioxide")),
            "air_ozone":       ozone,
            "air_so2":         safe_float(row.get("air_quality_Sulphur_dioxide")),
            "air_pm25":        pm25,
            "air_pm10":        safe_float(row.get("air_quality_PM10")),
            "air_epa_index":   epa,
            "air_defra_index": safe_int(row.get("air_quality_gb-defra-index")),
            "go_outside":      service.calculate_go_outside(epa, pm25, ozone),
        })

    repo.bulk_insert_air_quality(aq_records)
    print(f"AirQuality: {len(aq_records)} рядків вставлено")

    session.close()
    print("Завантаження завершено")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "init":
            alembic_upgrade_head()
            print("Міграції застосовано (head).")
        elif sys.argv[1] == "load":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
            load_csv_to_db(limit=limit)
        elif sys.argv[1] == "countries":
            session = Session()
            repo    = WeatherRepository(session)
            service = WeatherService(repo)
            cli     = WeatherCLI(service)
            cli.show_countries()
            session.close()
        elif sys.argv[1] == "migrate":
            from migrate_db import migrate_postgres_to_mysql
            migrate_postgres_to_mysql()
    else:
        session = Session()
        repo    = WeatherRepository(session)
        service = WeatherService(repo)
        cli     = WeatherCLI(service)
        try:
            cli.run()
        except EOFError:
            print("\nНемає вводу (stdin). Використайте команди:")
            print("  python main.py init")
            print("  python main.py load [limit]")
            print("  python main.py countries")
            print("  python main.py migrate")
        session.close()
