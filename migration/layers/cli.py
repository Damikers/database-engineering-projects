from layers.service import WeatherService

EPA_LEVELS = {
    1: "Good",
    2: "Moderate",
    3: "Unhealthy for Sensitive Groups",
    4: "Unhealthy",
    5: "Very Unhealthy",
    6: "Hazardous"
}


class WeatherCLI:
    def __init__(self, service: WeatherService):
        self.service = service

    def run(self):
        print("Weather & Air Quality Query")

        country  = input("\nКраїна (Ukraine): ").strip()
        date_str = input("Дата (YYYY-MM-DD): ").strip()
        epa_raw  = input(
            "Макс. EPA Index 1-6 (або Enter - без фільтру): "
        ).strip()
        epa_max = int(epa_raw) if epa_raw.isdigit() else None

        try:
            results = self.service.query_weather(country, date_str, epa_max)
        except ValueError as e:
            print(f"\nПомилка: {e}")
            return

        if not results:
            print("\nДані не знайдено.")
            return

        for i, r in enumerate(results, 1):
            print(f"\n{'─' * 50}")
            print(f"  Запис #{i}:  {r['country']}  |  {r['date']}")
            print(f"{'─' * 50}")
            print(f"  Схід сонця    : {r['sunrise']}")
            print(f"  Вітер         : {r['wind_kph']} км/год, "
                  f"{r['wind_degree']}° ({r['wind_dir']})")
            print()
            print(f"  Стан повітря:")
            print(f"    CO          : {r['air_co']} мкг/м³")
            print(f"    NO2         : {r['air_no2']} мкг/м³")
            print(f"    Ozone       : {r['air_ozone']} мкг/м³")
            print(f"    SO2         : {r['air_so2']} мкг/м³")
            print(f"    PM2.5       : {r['air_pm25']} мкг/м³")
            print(f"    PM10        : {r['air_pm10']} мкг/м³")
            epa = r['air_epa_index']
            print(f"    EPA Index   : {epa} ({EPA_LEVELS.get(epa, '?')})")
            print(f"    DEFRA Index : {r['air_defra_index']}")
            print()
            go = r['go_outside']
            if go is None:
                verdict = "Невідомо (немає даних)"
            elif go:
                verdict = "ТАК - повітря в нормі"
            else:
                verdict = "НІ - рівень забруднення небезпечний"
            print(f"  Чи виходити?  : {verdict}")

    def show_countries(self):
        countries = self.service.repo.get_all_countries()
        print("\nДоступні країни:")
        for c in countries:
            print(f"  {c}")