#My API
#----------------------
#import station

import numpy as np
from sqlalchemy.ext.automap import automap_base
import pandas as pd
import datetime as dt
import sqlite3
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_


from flask import Flask, jsonify
#--------------------
# Database Setup

engine = create_engine("sqlite:///resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

#save the references to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


#--------------------
# Flask Setup

app = Flask(__name__)


#---------------------
# Flask routes

#--------------------
#Welcome Page
@app.route("/")
def welcome():
    """List of all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Dates and temperature observations of the most active station for the last year of data: /api/v1.0/tobs<br/>"
        f"Temperature stat from the start date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature stat from start to end dates(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )


#-------------------
#Precipitation page

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    sel = [Measurement.date,Measurement.prcp]
    queryresult = session.query(*sel).all()
    session.close()
    
    precipitation = []
    for date, prcp in queryresult:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)
      
    return jsonify(precipitation)

#-----------------------
#Station page

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    sel = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    queryresult = session.query(*sel).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)

#----------------------------
#TOBS Page

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    lateststr = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latestdate = dt.datetime.strptime(lateststr, '%Y-%m-%d')
    querydate = dt.date(latestdate.year -1, latestdate.month, latestdate.day)
    sel = [Measurement.date,Measurement.tobs]
    queryresult = session.query(*sel).filter(Measurement.date >= querydate).all()
    session.close()

    tobs_query = []
    for date, tobs in queryresult:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobs_query.append(tobs_dict)

    return jsonify(tobs_query)

#------------------------------------
#Start date query page

@app.route('/api/v1.0/<date>/')
def given_date(date):
    session = Session(engine)
    results = session.query(func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date >= date).\
        group_by(Measurement.date).all()
    data_list = []
    for result in results:
        row = {}
        row['Start Date'] = date
        row['End Date'] = '2017-08-23'
        row['Average Temperature'] = result[0]
        row['Highest Temperature'] = result[1]
        row['Lowest Temperature'] = result[2]
        data_list.append(row)
    session.close()

    return jsonify(data_list)

#------------------------------------------------
#Start date/End date query page

@app.route('/api/v1.0/<start>/<stop>')
def temp_range_start_stop(start,stop):
    session = Session(engine)
    results = session.query(Measurement.date,\
                            func.min(Measurement.tobs),\
                            func.avg(Measurement.tobs),\
                            func.max(Measurement.tobs)).\
                            filter(and_(Measurement.date >= start, Measurement.date <= stop)).\
                            group_by(Measurement.date).all()

    tobs_query = []
    for date,min,avg,max in results:
        row = {}
        row['Date'] = date
        row['Lowest Temperature'] = min
        row['Average Temperature'] = avg
        row['Highest Temperature'] = max
        tobs_query.append(row)
    session.close()

    return jsonify(tobs_query)

#------------------------------
#Get the party started

if __name__ == '__main__':
    app.run(debug=True)