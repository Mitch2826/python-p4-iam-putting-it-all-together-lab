from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    #columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=True)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)
    
    #relationship
    recipes = db.relationship('Recipe', backref='user')
    
    #serializer
    serialize_rules = ("-recipes.user", "-_password_hash")
    
    #password hashing
    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")
    
    @password_hash.setter
    def password_hash(self, password):
        self._password_hash=bcrypt.generate_password_hash(password).decode('utf-8')
    
    #authentication method
    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)
    
    #validations
    @validates('username')
    def validate_username(self,key,value):
        if not value:
            raise ValueError("Username must be present.")
        return value

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    
    #columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    
    #serializer
    serialize_rules = ("-user.recipes",)
    
    #validations
    @validates('title')
    def validate_title(self,key,value):
        if not value:
            raise ValueError("Title must be present.")
        return value
    
    @validates('instructions')
    def validate_instructions(self,key,value):
        if not value or len(value) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return value