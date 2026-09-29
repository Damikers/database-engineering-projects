from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models.weather import Base

class AirQuality(Base):
    __tablename__ = "air_quality"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    weather_id     = Column(Integer, ForeignKey("weather.id"), nullable=False)

    air_co          = Column(Float,   nullable=True)
    air_no2         = Column(Float,   nullable=True)
    air_ozone       = Column(Float,   nullable=True)
    air_so2         = Column(Float,   nullable=True)
    air_pm25        = Column(Float,   nullable=True)
    air_pm10        = Column(Float,   nullable=True)
    air_epa_index   = Column(Integer, nullable=True)
    air_defra_index = Column(Integer, nullable=True)

    go_outside = Column(Boolean, nullable=True, default=None)

    weather = relationship("Weather", backref="air_quality_data")