"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route('/users/<int:user_id>')
def get_one_user(user_id):
    user = User.query.filter_by(id = user_id).one_or_none()
    if user is not None:
        return jsonify(user.serialize()), 200
    else:
        return jsonify({"msg": "user not found"}), 404

@app.route('/planets')
def get_all_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets])

@app.route('/planets/<int:planet_id>')
def get_single_planet(planet_id):
    search_planet = Planet.query.filter_by(id = planet_id).one_or_none()
    if search_planet != None:
        return jsonify(search_planet.serialize()), 200
    else:
        return jsonify({"msg": "planet was not found"}), 404

@app.route('/people')
def get_all_people():
    people = People.query.all()
    return jsonify([person.serialize() for person in people])

@app.route('/people/<int:people_id>')
def get_one_person(people_id):
    person = People.query.filter_by(id = people_id).one_or_none()
    if person is not None:
        return jsonify(person.serialize()), 200
    else:
        return jsonify({"msg": "person not found"}, 404)
    
@app.route('/login', methods=['POST'])
def login_user():
    email = request.json.get("email")
    password = request.json.get("password")

    user = User.query.filter_by(email = email, password=password).first()
    if user is None:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=user.email)
    return jsonify({"token": access_token, "identity": user.email})

@app.route('/users/favorites')
@jwt_required()
def get_favorites():
    current_user_email = get_jwt_identity()
    current_user = User.query.filter_by(email = current_user_email).first()
    return jsonify(current_user.serialize()), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST', 'DELETE'])
@jwt_required()
def add_or_delete_planet(planet_id):
    if request.method == 'POST':
        current_user_email = get_jwt_identity()
        current_user = User.query.filter_by(email = current_user_email).first()
        new_favorite = Favorite(user_id=current_user.id, planet_id=planet_id, people_id=None)

        if new_favorite.planet_id is None:
            return jsonify({"msg": "invalid planet id"}), 404
        
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify(current_user.serialize())
    else:
        current_user_email = get_jwt_identity()
        current_user = User.query.filter_by(email = current_user_email).first()
        current_favorite = Favorite.query.filter_by(user_id = current_user.id, planet_id=planet_id).first()

        if current_favorite is None:
            return jsonify({"msg": "invalid planet id"}), 404
        
        db.session.delete(current_favorite)
        db.session.commit()
        return jsonify(current_user.serialize())

@app.route('/favorite/people/<int:people_id>', methods=['POST', 'DELETE'])
@jwt_required()
def add_or_delete_char(people_id):
    if request.method == 'POST':
        current_user_email = get_jwt_identity()
        current_user = User.query.filter_by(email = current_user_email).first()     
        new_favorite = Favorite(user_id=current_user.id, planet_id=None, people_id=people_id)

        if current_favorite is None:
            return jsonify({"msg": "invalid character id"}), 404
        
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify(current_user.serialize())
    else:
        current_user_email = get_jwt_identity()
        current_user = User.query.filter_by(email = current_user_email).first()
        current_favorite = Favorite.query.filter_by(user_id = current_user.id, people_id=people_id).first()

        if current_favorite is None:
            return jsonify({"msg": "invalid planet id"}), 404
        
        db.session.delete(current_favorite)
        db.session.commit()
        return jsonify(current_user.serialize())

        

# @app.route('/users/<int:user_id>/favorites')
# def get_one_favorites(user_id):
#     user = User.query.filter_by(id = user_id).one_or_none()
#     if user is not None:
#         favorites = user.favorites
#         return jsonify([favorite.serialize() for favorite in favorites]), 200
#     else:
#         return jsonify({"msg": "user not found"}), 404
    

# this only runs if `$ python src/app.py` is executed
    
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
