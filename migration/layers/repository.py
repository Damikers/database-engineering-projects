from sqlalchemy.orm import Session
from sqlalchemy import select
from models.weather import Weather
from models.air_quality import AirQuality


class WeatherRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_country_and_date(self, country: str, date, epa_max: int = None):
        stmt = (
            select(Weather, AirQuality)
            .join(AirQuality, AirQuality.weather_id == Weather.id)
            .where(Weather.country == country)
            .where(Weather.last_updated == date)
        )
        if epa_max is not None:
            stmt = stmt.where(AirQuality.air_epa_index <= epa_max)

        return self.session.execute(stmt).all()

    def get_all_countries(self):
        stmt = select(Weather.country).distinct().order_by(Weather.country)
        return [r[0] for r in self.session.execute(stmt).all()]

    def bulk_insert_weather(self, records: list):
        self.session.bulk_insert_mappings(Weather, records)
        self.session.commit()

    def bulk_insert_air_quality(self, records: list):
        self.session.bulk_insert_mappings(AirQuality, records)
        self.session.commit()