# migrate_db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import POSTGRES_URL, MYSQL_URL
from models.weather import Base, Weather
from models.air_quality import AirQuality


def migrate_postgres_to_mysql():
    print("Починаємо міграцію")

    pg_engine    = create_engine(POSTGRES_URL)
    mysql_engine = create_engine(MYSQL_URL)

    Base.metadata.drop_all(mysql_engine)
    Base.metadata.create_all(mysql_engine)
    print("Схему створено в MySQL")

    PGSession    = sessionmaker(bind=pg_engine)
    MySQLSession = sessionmaker(bind=mysql_engine)

    pg_s    = PGSession()
    mysql_s = MySQLSession()

    BATCH = 500
    offset, total = 0, 0
    while True:
        rows = pg_s.query(Weather).offset(offset).limit(BATCH).all()
        if not rows:
            break
        for row in rows:
            pg_s.expunge(row)
            mysql_s.merge(row)
        mysql_s.commit()
        total  += len(rows)
        offset += BATCH
        print(f"  Weather: {total} рядків", end="\r")

    print(f"\nWeather перенесено: {total} рядків")

    offset, total = 0, 0
    while True:
        rows = pg_s.query(AirQuality).offset(offset).limit(BATCH).all()
        if not rows:
            break
        for row in rows:
            pg_s.expunge(row)
            mysql_s.merge(row)
        mysql_s.commit()
        total  += len(rows)
        offset += BATCH
        print(f"  AirQuality: {total} рядків...", end="\r")

    print(f"\nAirQuality перенесено: {total} рядків")

    pg_s.close()
    mysql_s.close()
    print("Міграція завершена. Обидві БД синхронізовані.")


if __name__ == "__main__":
    migrate_postgres_to_mysql()