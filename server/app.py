#!/usr/bin/env python3
from flask import Flask, request, jsonify, make_response
from flask_restful import Api
from models import db, Restaurant, Pizza, RestaurantPizza
from sqlalchemy.exc import SQLAlchemyError
import os
from flask_migrate import Migrate

# Create the Flask app object
app = Flask(__name__)

# Set up the app configuration and database URI
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

# Initialize the database
db.init_app(app)
migrate = Migrate(app, db)

# Initialize the Flask-RESTful API
api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# Define your API routes after the app is defined

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants])

@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        return jsonify({
            **restaurant.to_dict(),
            "restaurant_pizzas": [rp.to_dict() for rp in restaurant.pizzas]
        })
    return jsonify({"error": "Restaurant not found"}), 404

@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return make_response('', 204)
    return jsonify({"error": "Restaurant not found"}), 404

@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas])

@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    try:
        data = request.get_json()
        price = data.get("price")
        pizza_id = data.get("pizza_id")
        restaurant_id = data.get("restaurant_id")

        # Validate price
        if price < 1 or price > 30:
            return jsonify({"errors": ["Price must be between 1 and 30"]}), 400

        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)

        if pizza and restaurant:
            restaurant_pizza = RestaurantPizza(price=price, pizza=pizza, restaurant=restaurant)
            db.session.add(restaurant_pizza)
            db.session.commit()
            return jsonify(restaurant_pizza.to_dict()), 201
        return jsonify({"errors": ["Invalid pizza_id or restaurant_id"]}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 400

# Run the app
if __name__ == "__main__":
    app.run(port=5555, debug=True)
