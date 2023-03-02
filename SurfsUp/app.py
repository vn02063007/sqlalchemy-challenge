import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#### Setup Database ####

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# 1. Define homepage and list all available routes.

@app.route("/")
def welcome():
    """List all available API routes"""
    print("Server received request for 'Welcome' page...")
    return (
        f"Welcome to Hawaii Weather Data API!<br/>"
        f"All available Routes:<br/>"
        f"Daily Precipitation Totals for the Last 12 Months: /api/v1.0/precipitation<br/>"
        f"List of Weather Stations: /api/v1.0/stations<br/>"
        f"Temperature Observations for Most Active Station over Last 12 Months: /api/v1.0/tobs<br/>"
        f"Min, Average & Max Temperatures from Start Date: /api/v1.0/start<br/>"
        f"Min, Average & Max Temperatures for Date Range: /api/v1.0/start/end<br/>"
        f"NOTE: Please enter all 'start' and 'end' dates in yyyy-mm-dd format. For example: /api/v1.0/2012-07-01/2012-07-03."
    )



# 2. Convert the query results into a dictionary by using date as the key and prcp as the value. Return the json representation of your dictionary. 

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    
    query_date = '2016-08-23'
    
    sel = [Measurement.date,Measurement.prcp]
    pastyear_precip = session.query(*sel).\
        filter(Measurement.date >= query_date).\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()
    
    session.close()

    precipitation = []
    for date, prcp in pastyear_precip:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    print("Server received request for Daily Precipitation Totals for the Last 12 Months...")
    return jsonify(precipitation)



# 3. Return a json list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    sel = [Measurement.station]
    activestations = session.query(*sel).\
        group_by(Measurement.station).all()
    
    session.close()
    
    stationslist = list(np.ravel(activestations))
    
    print("Server received request for List of Weather Stations...")
    return jsonify(stationslist)



# 4. Query the dates and temperature observations of the most-active station for the previous year of data. Return a JSON list of temperature observations for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    query_date = '2016-08-23'
    sel = [Measurement.date, 
        Measurement.tobs]
    station_mostactive = session.query(*sel).\
            filter(Measurement.date >= query_date, Measurement.station == 'USC00519281').\
            group_by(Measurement.date).\
            order_by(Measurement.date).all()

    session.close()

    # Return a dictionary with the date as key and the daily temperature observation as value
    obs_dates = []
    obs_temperature = []

    for date, observation in station_mostactive:
        obs_dates.append(date)
        obs_temperature.append(observation)
    
    mostactive_tobs_dict = dict(zip(obs_dates, obs_temperature))

    print("Server received request for Temperature Observations for Most Active Station over Last 12 Months...")
    return jsonify(mostactive_tobs_dict)



#5. Return a JSON lost of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.

## For specified start, calculate min, avg, and max temperature for all the dates greater than or equal to the start date.

@app.route("/api/v1.0/<start>")
def onlystartdate(start):
    session = Session(engine)
    query_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    sumTemp = []
    for min,avg,max in query_result:
        temp_dict = {}
        temp_dict["Min"] = min
        temp_dict["Average"] = avg
        temp_dict["Max"] = max
        sumTemp.append(temp_dict)

    print("Server received request for Min, Average & Max Temperatures from Start Date...")
    return jsonify(sumTemp)



## For specified start date and end date, calcultate min, avg, and max temperature for all the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>/<end>")
def startenddate(start,end):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    sumTempRange = []
    for min,avg,max in queryresult:
        temp_dict = {}
        temp_dict["Min"] = min
        temp_dict["Average"] = avg
        temp_dict["Max"] = max
        sumTempRange.append(temp_dict)

    print("Server received request for Min, Average & Max Temperatures from Date Range...")
    return jsonify(sumTempRange)



if __name__ == "__main__":
    app.run(debug=True)