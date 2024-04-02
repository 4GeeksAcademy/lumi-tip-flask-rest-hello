from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "favorites": [favorite.serialize() for favorite in self.favorites] if self.favorites else None
        }

class Planet(db.Model):
    __tablename__ = "planets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    population = db.Column(db.Integer, nullable=False)
    diameter = db.Column(db.Integer, nullable=False)
    climate = db.Column(db.String, nullable=False)
    terrain = db.Column(db.String, nullable=False)

    def __init__(self, name, population, diameter, climate, terrain):
        self.name = name
        self.population = population
        self.diameter = diameter
        self.climate = climate
        self.terrain = terrain

    def __repr__(self):
        return '<Planet %r>' % self.name
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population,
            "diameter": self.diameter,
            "climate": self.climate,
            "terrain": self.terrain,
            "residents": [resident.serialize() for resident in self.residents],
        }

class People(db.Model):
    __tablename__ = "people"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    hair_color = db.Column(db.String, unique=False, nullable=False)
    skin_color = db.Column(db.String, unique=False, nullable=False)
    gender = db.Column(db.String, unique=False, nullable=False)
    homeworld_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    homeworld = db.relationship(Planet, backref = "residents")

    def __init__(self, name, hair_color, skin_color, gender):
            self.name = name
            self.hair_color = hair_color
            self.skin_color = skin_color
            self.gender = gender
        
    def __repr__(self):
        return '<People %r>' % self.name
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "hair_color": self.hair_color,
            "skin_color": self.skin_color,
            "gender": self.gender,
        }

class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship(User, backref = "favorites")

    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=True)
    planet = db.relationship(Planet, backref = "favorites")

    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=True)
    people = db.relationship(People, backref = "favorites")

    def __repr__(self):
        return '<Favorite %r>' % self.id
    
    def serialize(self):
        return{
            "id": self.id,
            "user": self.user.email,
            "planet": self.planet.name if self.planet else None,
            "people": self.people.name if self.people else None
        }
