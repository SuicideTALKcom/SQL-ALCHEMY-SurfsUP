import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import inspect
from sqlalchemy import and_, or_, not_

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite?check_same_thread=False")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)   

#################################################
# Flask Routes
#################################################
@app.route('/')
def home():
    return (
        f"Available Routes<br><br/>"

        f"List of Obervation Stations:<br/>"
        f"/api/v1.0/stations/<br><br/>" 

        f"Last 12 Months of Precipitation:<br/>"
        f"/api/v1.0/precipitation/<br><br/>" 

        f"Last 12 Months of Temperature:<br/>"
        f"/api/v1.0/tobs/<br><br/>"

        f"Minimum, Average, and Maximum Temperatures from Start Date:<br/>"
        f"/api/v1.0/2016-01-01/<br><br/>"

        f"Minimum, Average, and Maximum Temperatures from Date Range:<br/>"
        f"/api/v1.0/2016-01-01/2016-12-31/")

# Query all Stations
# Convert into normal list
@app.route('/api/v1.0/stations/')
def stations():
    results = session.query(Station.station).all()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

# Query Last 12 Months of Precipitation for all Stations
# Create Dictionary from row data and append to list of all_dates
@app.route('/api/v1.0/precipitation/')
def precipitation():
    results2 = session.query(Measurement.date, Measurement.prcp).\
    filter(and_(Measurement.date<='2017-08-23', Measurement.date>='2016-08-24')).\
    order_by(Measurement.date).all()

    all_dates = {date:prcp for date, prcp in results2}
 
    return jsonify(all_dates)

# Query Last 12 Months of Temperature for all Stations
# Create Dictionary from row data and append to list of all_dates
@app.route('/api/v1.0/tobs/')
def tobs():
    results3 = session.query(Measurement.date, Measurement.tobs).\
    filter(and_(Measurement.date<='2017-08-23', Measurement.date>='2016-08-24')).\
    order_by(Measurement.date).all()

    all_dates2 = {date:tobs for date, tobs in results3}

    return jsonify(all_dates2)

# Return a JSON-list of Temperature Observations from the previous year.
# Return JSON list of temps: minimum, average, maximum as TMIN TAVG TMAX for a specific date
@app.route('/api/v1.0/<start>/')
def temps(start):

   results4 = session.query(func.min(Measurement.tobs), 
        func.avg(Measurement.tobs), 
        func.max(Measurement.tobs)).filter(Measurement.date >= start).all()

   combined_temps = list(np.ravel(results4))
   session.close()

   return jsonify(combined_temps)

# Return a JSON-list of Temperature Observations from the previous year.
# Return JSON list of temps: minimum, average, maximum as TMIN TAVG TMAX for a date range
@app.route("/api/v1.0/<start>/<end>/")
def temps2(start,end):

   results5 = session.query(func.min(Measurement.tobs), 
        func.avg(Measurement.tobs), 
        func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

   combined_temps2 = list(np.ravel(results5))
   session.close()
   
   return jsonify(combined_temps2)

app.run(debug=True)