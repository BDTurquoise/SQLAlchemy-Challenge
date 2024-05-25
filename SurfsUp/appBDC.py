# Import the dependencies.

from flask import Flask, jsonify
import numpy as np
import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

app = Flask(__name__)

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# Assign the measurement classes to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

#################################################
# Flask Routes
#################################################
# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Use the last data point in the database to calculate the date 1 year ago
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_year = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query the last year for date and precipitation 
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year).all()

    # Store query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    results = session.query(Station.station).all()

    # Store query results to a list
    stations_list = list(np.ravel(results))

    return jsonify(stations_list)

# Tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # Use the last data point in the database to calculate the date 1 year ago
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_year = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query temp observations for the last year from the most active station 
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= last_year).all()

    # Store query results to a list
    tobs_list = list(np.ravel(tobs_data))

    return jsonify(tobs_list)

# Start route
@app.route("/api/v1.0/<start>")
def start(start):
    # Query min, max, average temps from the start date to the end of the data
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # Store query results to a list
    temps_list = list(np.ravel(temps))

    return jsonify(temps_list)

# Start/end route
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Query min, max, average temps from start date to end date
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Store query results to a list
    temps_list = list(np.ravel(temps))

    return jsonify(temps_list)

if __name__ == '__main__':
    app.run(debug=True)