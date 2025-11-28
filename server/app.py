#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()
        
        username = data.get("username")
        password = data.get("password")
        image_url = data.get("image_url")
        bio = data.get("bio")
        
        try:
            
            new_user = User(
                username=username,
                image_url=image_url,
                bio=bio
            )
        
            # set password using the password_hash setter
            new_user.password_hash = password
        
        
            db.session.add(new_user)
            db.session.commit()
        except ValueError as e:
            return {"errors": str(e)}, 422
        
        except IntegrityError:
            db.session.rollback()
            return {"errors": "Username already exists."}, 422
        
        #Log user in by storing their id in session
        session['user_id'] = new_user.id
        
        return new_user.to_dict(), 201
        

class CheckSession(Resource):
    def get(self):
        user_id= session.get('user_id')
        if not user_id:
            return {"errors": "Unauthorized"}, 401
        
        user = db.session.get(User, user_id)
        if not user:
            #if user id in session but not found in db
            return {"errors": "Unauthorized"}, 401
        
        return user.to_dict(), 200

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.authenticate(password):
            session["user_id"] = user.id
            return user.to_dict(), 200
        else:
            return {"errors": "Invalid username or password"}, 401

class Logout(Resource):
    def delete(self):
        user_id = session.get('user_id')
        
        if not user_id:
            return {"error": "Unauthorized"}, 401
            
        session.pop('user_id', None)
        return {}, 204

class RecipeIndex(Resource):
    def get(self):
        if not session.get('user_id'):
            return {"errors": "Unauthorized"}, 401
        
        recipes = Recipe.query.all()
        
        recipes_dict = [recipe.to_dict(rules=('-user.recipes',)) for recipe in recipes]
        return recipes_dict, 200
    
    def post(self):
        if not session.get('user_id'):
            return{"errors": "Unauthorized"}, 401
        
        data = request.get_json()
        try:
            new_recipe = Recipe(
                title=data.get("title"),
                instructions=data.get("instructions"),
                minutes_to_complete=data.get("minutes_to_complete"),
                user_id=session["user_id"]
            )
        
        
            db.session.add(new_recipe)
            db.session.commit()
            
        except ValueError as ve:
            db.session.rollback()
            return {"errors": str(ve)}, 422
        
        except Exception as e:
            db.session.rollback()
            # return validation errors
            return {"errors": str(e)}, 422
        
        return new_recipe.to_dict(rules=('-user.recipes',)), 201        

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)