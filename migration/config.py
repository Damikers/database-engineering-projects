from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

POSTGRES_URL = os.getenv(
    "POSTGRES_URL",
    "postgresql+psycopg2://postgres:change_me@localhost:5432/weather_db",
)

MYSQL_URL = os.getenv(
    "MYSQL_URL",
    "mysql+pymysql://root:change_me@localhost/weather_db",
)

DATABASE_URL = os.getenv("DATABASE_URL", POSTGRES_URL)

CSV_PATH = os.getenv("CSV_PATH", str(BASE_DIR / "GlobalWeatherRepository.csv"))
