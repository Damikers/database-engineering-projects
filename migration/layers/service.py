from datetime import datetime
from layers.repository import WeatherRepository


class WeatherService:
    def __init__(self, repo: WeatherRepository):
        self.repo = repo

    def calculate_go_outside(self, epa_index, pm25, ozone) -> bool:
        epa_index = epa_index if epa_index is not None else 99
        pm25      = pm25      if pm25      is not None else 999
        ozone     = ozone     if ozone     is not None else 999
        return bool(epa_index <= 3 and pm25 < 35 and ozone < 180)

    def query_weather(self, country: str, date_str: str,
                      epa_max: int = None) -> list:
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Невірний формат дати. Використовуйте YYYY-MM-DD")

        rows = self.repo.get_by_country_and_date(country, date, epa_max)
        if not rows:
            return []

        results = []
        for weather, aq in rows:
            results.append({
                "country":         weather.country,
                "date":            str(weather.last_updated),
                "sunrise":         str(weather.sunrise) if weather.sunrise else "—",
                "wind_kph":        weather.wind_kph,
                "wind_degree":     weather.wind_degree,
                "wind_dir":        weather.wind_dir.value if weather.wind_dir else "—",
                "air_co":          aq.air_co,
                "air_no2":         aq.air_no2,
                "air_ozone":       aq.air_ozone,
                "air_so2":         aq.air_so2,
                "air_pm25":        aq.air_pm25,
                "air_pm10":        aq.air_pm10,
                "air_epa_index":   aq.air_epa_index,
                "air_defra_index": aq.air_defra_index,
                "go_outside":      aq.go_outside,
            })
        return results