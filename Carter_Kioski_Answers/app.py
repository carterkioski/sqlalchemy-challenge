import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
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

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        "Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/&#60;start&#62;<br>"
        f"/api/v1.0/&#60;start&#62;/&#60;end&#62;<br>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()
    
    percp = list(np.ravel(results))
    return jsonify(percp)



@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()

    session.close()

    stations = list(np.ravel(results))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    for row in session.query(Measurement).order_by(Measurement.date.desc()).limit(1):
        recent=dt.datetime.strptime(row.date, '%Y-%m-%d')
    one_year = recent -dt.timedelta(365)
    top = session.query(Station.station).filter(Measurement.station == Station.station).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    results = session.query(Measurement.tobs).order_by(Measurement.date.desc()).filter(Measurement.date >= one_year).filter(Measurement.station == top[0][0]).all()
    session.close()

    tobs = list(np.ravel(results))
    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    start_date = dt.datetime.strptime(start,'%Y-%m-%d')
    results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    session.close()

    start_temps = list(np.ravel(results))
    return jsonify(start_temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    session = Session(engine)
    start_date = dt.datetime.strptime(start,'%Y-%m-%d')
    end_date = dt.datetime.strptime(end,'%Y-%m-%d')

    results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()

    start_end_temps = list(np.ravel(results))
    return jsonify(start_end_temps)

if __name__ == '__main__':
    app.run(debug=True)
