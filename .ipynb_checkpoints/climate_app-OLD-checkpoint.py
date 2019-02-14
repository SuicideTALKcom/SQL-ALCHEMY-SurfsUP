import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the invoices and invoice_items tables
Measurements = Base.classes.Measurements
    
Station = Base.classes.Station
    

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
    
    return (
            f"Here are all the API:<br/>"
            f"Available Routes:<br/>"
            
            f"/api/v1.0/precipitation/&ltdate&gt<br/>"
            f"dates and temperature observations from the last year <br/>"
            
            f"/api/v1.0/stations<br/>"
            f"list of stations <br/>"
            
            f"/api/v1.0/tobs/&ltyear&gt <br/>"
            f"list of Temperature Observations (tobs) for the previous year <br/>"
            
            
            f"/api/v1.0/&ltstart_date&gt<br/>"
            f"list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range <br/>"
            
            f"/api/v1.0/&ltstart_date&gt/&ltend_date&gt<br/>"
            f"list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range <br/>"
        )
# Routes /api/v1.0/precipitation
# Query for the dates and temperature observations from the last year.
# Convert the query results to a Dictionary using date as the key and tobs as the value.
# Return the json representation of your dictionary.  

@app.route("/api/v1.0/precipitation/<date>")
def Temp_last(date) :
    
    day = pd.to_numeric(pd.to_datetime(date).strftime("%d"))
    month= pd.to_numeric(pd.to_datetime(date).strftime("%m"))
    year = pd.to_numeric(pd.to_datetime(date).strftime("%Y"))
    
    Year = pd.to_numeric((dt.datetime(year, month, day) - dt.timedelta(days=365)).strftime("%Y"))
    Month= pd.to_numeric((dt.datetime(year, month, day) - dt.timedelta(days=365)).strftime("%m"))
    Day= pd.to_numeric((dt.datetime(year, month, day) - dt.timedelta(days=365)).strftime("%d"))
    
    previous_year = dt.datetime(Year, Month, Day).strftime("%Y-%m-%d")
    
    result1 = session.query(Measurements.date).\
           filter(Measurements.date >= previous_year).all()
    
    result2 = session.query( Measurements.tobs).\
           filter(Measurements.date >= previous_year).all()
    key = list(np.ravel(result1))
    value = list(np.ravel(result2))
    dictionary = dict(zip(key, value))

    return jsonify(dictionary)

@app.route("/api/v1.0/stations")
def station() :
    json_dict = {}
    results = session.query(Station.station).all()
    json_dict["stations"] = list(np.ravel(results))

    return jsonify(json_dict)
    
    
# Return a json list of Temperature Observations (tobs) for the previous year    
@app.route("/api/v1.0/tobs")
@app.route("/api/v1.0/tobs/<year>")
def Temp_pre(year) :
    year = pd.to_numeric(year)-1
    if (year >= 2010 and year <= 2017):
        tob = {}
        year_str =str(year) 
        tob_results = session.query(Measurements.tobs).filter(Measurements.date.contains(year_str)).all()
        tob["Temperature Observations"] = list(np.ravel(tob_results))
    return jsonify(tob)
    
# Return a json list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.


@app.route("/api/v1.0/<start_date>")
def Temp_info(start_date):
    
    json_dict = {}
    avg = session.query(func.avg(Measurements.prcp)).\
           filter(Measurements.date >= start_date).all()
            
    minimum = session.query( func.min(Measurements.prcp) ).\
           filter(Measurements.date >= start_date).all()
    maximum = session.query( func.max(Measurements.prcp) ).\
           filter(Measurements.date >= start_date).all()
        
    json_dict['Average']= avg
    json_dict["Min"]= minimum
    json_dict["Max"]= maximum
    
    return jsonify(json_dict)

@app.route("/api/v1.0/<start_date>/<end_date>")
def Temp_info2(start_date, end_date):
    
    json_dict = {}
    avg = session.query(func.avg(Measurements.prcp)).\
           filter(Measurements.date >= start_date).\
           filter(Measurements.date <= end_date).all()
            
            
    minimum = session.query( func.min(Measurements.prcp) ).\
           filter(Measurements.date >= start_date).\
           filter(Measurements.date <= end_date).all()
            
    maximum = session.query( func.max(Measurements.prcp) ).\
          filter(Measurements.date >= start_date).\
          filter(Measurements.date <= end_date).all()
            
        
    json_dict['Average']= avg
    json_dict["Min"]= minimum
    json_dict["Max"]= maximum
    
    return jsonify(json_dict)
    
if __name__ == "__main__":
    
app.run(debug = True)