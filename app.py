# Import the dependencies.
import datetime as dt
from re import M
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


# reflect an existing database into a new model
# engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# base
Base = automap_base()
Base.prepare(autoload_with=engine, reflect=True)

# Save references to each table
# reflect the tables

measurement=Base.classes.measurement
station = Base.classes.station





# Create our session (link) from Python to the DB


#################################################
# Flask Setup

# create app
app = Flask(__name__)
#################################################





#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
     """List all available api routes."""
    return(
        
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    '''
    This gives the precipitation in json format for date and precipitation in the last year
    '''
    session = Session(engine)
    
    lastdate = session.query(func.max(measurementeasurement.date)).\
                    scalar()
    dt_lastdate= dt.datetime.strptime(lastdate,"%Y-%m-%d").date()
    dt_startdate = dt_lastdate - dt.timedelta(days=365)
    startdate = dt_startdate.strftime("%Y-%m-%d")
    results = session.query(measurement.date, measurement.prcp).\
            filter(measurement.date.between(startdate,lastdate)).\
            all()
    
    recip = []
    for date, prcp in results:
            precip_dict ={}
            precip_dict['date'] = date
            precip_dict['prcp'] = prcp
            precip.append(precip_dict)
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    '''
    This will provide a list of stations available
    '''
    session = Session(engine)

    results = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    '''
    This will give the temperatures and dates for the lastyear for the station
    with the largest amount of observations
    '''
    session = Session(engine)

    top_station = session.query(measurement.station).\
                    group_by(measurement.station).\
                    order_by(func.count(measurement.station).desc()).\
                    subquery()

    lastdate = session.query(func.max(measurement.date)).\
                    scalar()
    dt_lastdate= dt.datetime.strptime(lastdate,"%Y-%m-%d").date()
    dt_startdate = dt_lastdate - dt.timedelta(days=365)
    startdate = dt_startdate.strftime("%Y-%m-%d")
    
    results = session.query(measurement.date, measurement.tobs).\
                filter(measurement.date.between(startdate,lastdate)).\
                filter(measurement.station.in_(top_station)).\
                all()
    session.close()

    topStation = []
    for date, tobs in results:
            tobs_dict ={}
            tobs_dict['date'] = date
            tobs_dict['tobs'] = tobs
            topStation.append(tobs_dict)
    return jsonify(topStation)


    session.close()


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def rangestart(start,end=None):
    session=Session(engine)
    if end == None:
        enddate = session.query(func.max(measurement.date)).\
                    scalar()
    else:
        enddate = str(end)
    startdate = str(start)
    results = session.query(func.min(measurement.tobs).label('min_temp'),
                            func.avg(measurement.tobs).label('avg_temp'),
                            func.max(measurement.tobs).label('max_temp')).\
                filter(Measurement.date.between(startdate,enddate)).\
                first()
    session.close()
    datapoints = list(np.ravel(results))
    return jsonify(datapoints)



# boilerplate
if __name__ == "__main__":
    app.run(debug=True)
