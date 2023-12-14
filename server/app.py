#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

# CAMPER ROUTES #

@app.get('/campers')
def get_campers():
    campers = Camper.query.all()
    data = [ camper.to_dict( rules=('-signups',) ) for camper in campers ]
    return data, 200


@app.get('/campers/<int:id>')
def get_camper_by_id(id):
    # camper = db.session.get(Camper, id)
    camper = Camper.query.filter(Camper.id == id).first()
    if camper:
        return camper.to_dict(), 200
    else:
        return { "error": "Camper not found" }, 404
    

@app.patch('/campers/<int:id>')
def patch_camper_by_id(id):
    data = request.json
    found_camper = Camper.query.filter(Camper.id == id).first()
    if found_camper:
        try:
            for key in data:
                setattr(found_camper, key, data[key])
            db.session.add(found_camper)
            db.session.commit()
            return found_camper.to_dict(), 202
        except Exception as e:
            return {"error": f"{e}"}, 405 
    
    else:
        return { "error": "Camper not found" }, 404


@app.post('/campers')
def create_camper():
    data = request.json
    try:
        new_camper = Camper()
        for key in data:
            setattr(new_camper, key, data[key])
        db.session.add(new_camper)
        db.session.commit()
        return new_camper.to_dict(), 201
    except Exception as e:
        return { "error": f"{e}" }, 406


# ACTIVITIES ROUTES #

@app.get('/activities')
def get_activities():
    activities = Activity.query.all()
    activities_to_dict = [ a.to_dict( rules=['-signups'] ) for a in activities ]
    return activities_to_dict, 200


@app.delete('/activities/<int:id>')
def delete_activity(id):
    found_activity = Activity.query.filter(Activity.id == id).first()
    if found_activity:
        db.session.delete(found_activity)
        db.session.commit()
        return {}, 204
    else:
        return { 'message': 'Activity not found' }, 404


# SIGNUPS ROUTES #

@app.post('/signups')
def create_signup():
    data = request.json
    try:
        new_signup = Signup(
            time=data.get('time'),
            activity_id=data.get('activity_id'),
            camper_id=data.get('camper_id')
        )
        db.session.add(new_signup)
        db.session.commit()
        return new_signup.to_dict(), 201
    except Exception as e:
        return { 'error': f"{e}" }, 406


if __name__ == '__main__':
    app.run(port=5555, debug=True)
