# import dependencies 
import datetime as dt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float 
from sqlalchemy import exc
from sqlalchemy import event
from sqlalchemy import select

# Sets an object to utilize the default declarative base in SQL Alchemy
Base = declarative_base()

# SQLAlchemy ORM, tables cannot be mapped without a primary key 

# Creates Classes which will serve as the anchor points for our Tables by creating a priary key
class station(Base):
    __tablename__ = 'station'
    id = Column(Integer, primary_key=True)
    station = Column(String(255))
    name = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    elevation = Column(Float)
    
# Creates Classes which will serve as the anchor points for our Tables by creating a priary key
class measurement(Base):
    __tablename__ = 'measurement'
    id = Column(Integer, primary_key=True)
    station = Column(String(255))
    date = Column(String(255))
    prcp = Column(Float)
    tobs = Column(Float)

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///resources/hawaii.sqlite", pool_pre_ping=True)
conn = engine.connect()

# Create (if not already in existence) the tables associated with our classes.
Base.metadata.create_all(engine)

# Session is a temporary binding to our DB
session = Session(bind=engine)

# Reflect Database into ORM classes
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

# Save reference to the table
measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- List of prior year rain totals from all station<br/>"
        f"<br/>"
        f"/api/v1.0/station<br/>"
        f"- List of Station numbers and names<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- List of prior year temperatures from all station<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f"- When given the start date (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start date<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"
        f"- When given the start and the end date (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates between the start and end date inclusive<br/>"

    )

#########################################################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of rain fall for prior year"""
#    Query for the dates and precipitation observations from the last year.
#    Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
#    Return the json representation of your dictionary.
#    Create our session (link) from Python to the DB
    session = Session(engine)

    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    rain = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date > last_year).\
        order_by(measurement.date).all()
    
    session.close()

# Create a list of dicts with `date` and `prcp` as the keys and values
    rain_totals = []
    for result in rain:
        row = {}
        row["date"] = rain[0]
        row["prcp"] = rain[1]
        rain_totals.append(row)

    return jsonify(rain_totals)

#########################################################################################
@app.route("/api/v1.0/station")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    station_query = session.query(Station.name, Station.station)
    station = pd.read_sql(station_query.statement, station_query.session.bind)
    return jsonify(station.to_dict())

    session.close()

#########################################################################################
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperatures for prior year"""
#   Query for the dates and temperature observations from the last year.
#   Convert the query results to a Dictionary using `date` as the key and `tobs` as the value.
#   Return the json representation of your dictionary.
#   Create our session (link) from Python to the DB
    session = Session(engine)

    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temperature = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date > last_year).\
        order_by(measurement.date).all()
    
    session.close()

# Create a list of dicts with `date` and `tobs` as the keys and values
    temperature_totals = []
    for result in temperature:
        row = {}
        row["date"] = temperature[0]
        row["tobs"] = temperature[1]
        temperature_totals.append(row)

    return jsonify(temperature_totals)

#########################################################################################
@app.route("/api/v1.0/<start>")
def trip1(start):
# Create our session (link) from Python to the DB
    session = Session(engine)
 # go back one year from start date and go to end of data for Min/Avg/Max temp   
    start_date= dt.datetime.strptime('2016-08-23', '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = dt.date(2016, 8, 23)
    end =  dt.date(2017, 8, 23)
    trip_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

    session.close()  

#########################################################################################
@app.route("/api/v1.0/<start>/<end>")
def trip2(start,end):
# Create our session (link) from Python to the DB
    session = Session(engine)
  # go back one year from start/end date and get Min/Avg/Max temp     
    start_date= dt.datetime.strptime('2016-08-23', '%Y-%m-%d')
    end_date= dt.datetime.strptime('2017-08-23','%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = dt.date(2016, 8, 23)
    end =  dt.date(2017, 8, 23)
    trip_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

    session.close()

#########################################################################################

if __name__ == "__main__":
    app.run(debug=True)