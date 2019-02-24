import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
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

# Home Page - list all available routes
@app.route("/")
def welcome():
    return (
        f"<h2>Welcome to the Climate API!</h2>"
        f"<p><strong>Available routes:</strong></p>"
        f"<ul>"
        f"<li>/api/v1.0/precipitation</li>"
        f"<li>/api/v1.0/stations</li>"
        f"<li>/api/v1.0/tobs</li>"
        f"</ul>"
        f"<hr/>"
        f"<p>You can also get the min, avg, and max temps for a given start date or start-end date range<br/>"
        f"(replace <em>start-date</em> and/or <em>end-date</em> with a date formatted 'YYYY-MM-DD'):</p>"
        f"<ul>"
        f"<li>/api/v1.0/<em>start-date</em></li>"
        f"<li>/api/v1.0/<em>start-date</em>/<em>end-date</em></li>"
        f"</ul>"
    )

# Precipitation data from the dataset
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Query 'measurement' table for date and precipitation score
    results = (session.query(Measurement.date, Measurement.prcp).all())

    # Convert the query results to a Dictionary using date as the key and prcp as the value
    precipitation = []
    for item in results:
        precipitation_dict = {}
        precipitation_dict[item.date] = item.prcp
        precipitation.append(precipitation_dict)

    return jsonify(precipitation)

# List of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():

    # Query all stations from 'station' table
    results = session.query(Station.name).order_by(Station.name).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

# Dates and temperature observations from a year from the last data point
@app.route("/api/v1.0/tobs")
def tobs():

    # Calculate the date 1 year ago from the last data point in the database
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year = int(most_recent_date[0][:4])
    month = int(most_recent_date[0][5:7])
    day = int(most_recent_date[0][8:])
    query_date = dt.date(year, month, day) - dt.timedelta(days=365.25)
    
    # Query 'measurement' table for date and temperature observation
    results = (session
            .query(Measurement.date, Measurement.prcp)
            .filter(Measurement.date >= query_date)
            .order_by(Measurement.date)
            .all())

    return jsonify(results)

# Calculate the minimum temperature, the average temperature, and the max temperature for a given start date
@app.route("/api/v1.0/<start>")
def calc_temps(start):

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results = (session
                .query(*sel)
                .filter(Measurement.date >= start)
                .all())
    
    return jsonify(results)

# Calculate the minimum temperature, the average temperature, and the max temperature for a given start-end date range
@app.route("/api/v1.0/<start>/<end>")
def calc_temps_range(start, end):

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results = (session
                .query(*sel)
                .filter(Measurement.date >= start)
                .filter(Measurement.date <= end)
                .all())
    
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)