from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities_table'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    # RELATIONSHIPS #

    signups = db.relationship('Signup', back_populates='activity', cascade='all, delete-orphan')
    campers = association_proxy('signups', 'camper')
    
    # SERIALIZER RULES

    serialize_rules = ('-signups.activity',)
    
    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers_table'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)

    # RELATIONSHIPS #

    signups = db.relationship('Signup', back_populates='camper', cascade='all, delete-orphan')
    activities = association_proxy('signups', 'activity')

    # Add serialization rules

    serialize_rules = ('-signups.camper',)
    
    # VALIDATIONS #

    @validates('age')
    def validate_age(self, key, val):
        if 8 <= val <= 18:
            return val
        else:
            raise ValueError('Age must be between 8 and 18')
    
    
    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups_table'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)

    camper_id = db.Column(db.Integer, db.ForeignKey('campers_table.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities_table.id'), nullable=False)

    # RELATIONSHIPS #

    camper = db.relationship('Camper', back_populates='signups')
    activity = db.relationship('Activity', back_populates='signups')
    
    # Add serialization rules

    serialize_rules = ('-activity.signups', '-camper.signups')
    
    #  VALIDATIONS #

    @validates('time')
    def validate_time(self, key, val):
        if 0 <= val <= 23:
            return val
        else:
            raise ValueError('Time must be between 0 and 23')
    
    def __repr__(self):
        return f'<Signup {self.id}>'


# add any models you may need.
