# Importing needed modules
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
import datetime as dt
from dateutil.relativedelta import relativedelta
from datetime import datetime
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def landing():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/[Enter Start Date]  <br/>"
        f"/api/v1.0/[Enter Start Date]/[Enter End Date]"
    )
@app.route("/api/v1.0/precipitation")
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
    results = session.query(Measurement.station,Measurement.date, Measurement.prcp).all()

    session.close()

    prcp_data = []
    for station, date, prcp in results:
        res = {}
        res["station"] = station
        res["date"] = date
        res["prcp"] = prcp
        prcp_data.append(res)

    return jsonify(prcp_data)
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    """Return a list of passenger data including the name, age, and sex of each passenger"""
    results = session.query(Station.station).all()

    session.close()

    station_info = list(np.ravel(results))

    return jsonify(station_info)
@app.route("/api/v1.0/tobs")
def temp_obs():
    session = Session(engine)
    latest_date = session.query(Measurement.date).order_by(desc(Measurement.date)).first()
    date_range = dt.datetime.strptime(latest_date[0],'%Y-%m-%d') - relativedelta(years=1)

    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > date_range).group_by(Measurement.date)

    retults_dict = [{
        "date": r[0],
        "temperature": r[1],
    } 
    for r in results.all()]
    session.close()
    return jsonify(retults_dict)
@app.route("/api/v1.0/<start>")
def calc_temps_start(start):

    session = Session(engine)

    station_cal = [func.min(Measurement.prcp), 
       func.max(Measurement.prcp), 
       func.avg(Measurement.prcp)] 

    results = session.query(*station_cal).filter(Measurement.date >= start).all()  

    session.close()

    res = []
    for min_prcp, avg_prcp, max_prcp in results:
        precip_dates = {}
        precip_dates["min_prec"] = min_prcp
        precip_dates["avg_prec"] = avg_prcp
        precip_dates["max_prec"] = max_prcp
        res.append(precip_dates)

    return jsonify(res)
@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    station_cal = [func.min(Measurement.prcp), 
       func.max(Measurement.prcp), 
       func.avg(Measurement.prcp)] 

    results = session.query(*station_cal).filter(Measurement.date >= start).filter(Measurement.date <= end).all()  

    session.close()

    res = []
    for min_prcp, avg_prcp, max_prcp in results:
        precip_dates = {}
        precip_dates["min_prec"] = min_prcp
        precip_dates["avg_prec"] = avg_prcp
        precip_dates["max_prec"] = max_prcp
        res.append(precip_dates)

    return jsonify(res)



if __name__ == '__main__':
    app.run(debug=True)