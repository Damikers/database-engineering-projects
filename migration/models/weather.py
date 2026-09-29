import enum
from sqlalchemy import Column, Integer, String, Float, Date, Time, Enum
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class WindDirection(enum.Enum):
    N   = "N";   NNE = "NNE"; NE  = "NE";  ENE = "ENE"
    E   = "E";   ESE = "ESE"; SE  = "SE";  SSE = "SSE"
    S   = "S";   SSW = "SSW"; SW  = "SW";  WSW = "WSW"
    W   = "W";   WNW = "WNW"; NW  = "NW";  NNW = "NNW"

class Weather(Base):
    __tablename__ = "weather"

    id           = Column(Integer, primary_key=True, autoincrement=True)

    # Обов'язкові типи згідно завдання:
    country      = Column(String(100), nullable=False)
    wind_degree  = Column(Integer,     nullable=True)
    wind_kph     = Column(Float,       nullable=True)
    wind_dir     = Column(
        Enum(WindDirection, name="wind_direction_enum", native_enum=False),
        nullable=True
    )                                                    
    last_updated = Column(Date,        nullable=False)
    sunrise      = Column(Time,        nullable=True)
