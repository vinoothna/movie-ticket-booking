from flask import Flask, jsonify, request, session
from flask_bcrypt import Bcrypt

from pymongo import MongoClient
from datetime import datetime
from bson import json_util, ObjectId
import json
import os
import sys, traceback
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

client = MongoClient(os.getenv("MONGO_URL"))
db = client.bookmyshow


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

bcrypt = Bcrypt(app)



@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"Error":str(e)}), 404


@app.route('/', methods=['GET'])
def home():
    return jsonify({"message":"HomePage"}), 200



@app.route('/logout', methods=['POST'])
def logout():
    try:
        db.session_info.insert_one({"user_id":ObjectId(session["user_id"]),"action":"logout","time":datetime.now()})
        session.pop('user_id', None)
        session["logged_in"] = False
        return jsonify({"message":"Successfully Logged Out!"}), 200
    
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        return jsonify({"Exception":str(traceback.extract_tb(exc_traceback))}), 500


@app.route('/login', methods=['POST'])
def login():
    try:
        email = request.form['email']
        password = request.form['password']

        if(email in [None,""] or password in [None,""]):
            return jsonify({'message':"Email or Password cannot be empty"}), 401
        else:
            usr = db.user.find_one({"email":email})
            if(usr):
                if(bcrypt.check_password_hash(usr["password"], password)):
                    db.session_info.insert_one({"user_id":usr["_id"],"action":"login","time":datetime.now()})
                    session["user_id"] = str(usr["_id"])
                    session["logged_in"] = True
                    return jsonify({'message':"Login Successful"}), 200
                else:
                    return jsonify({'message':"Invalid Credential! Try Again!"}), 401
            else:
                return jsonify({'message':"Please signup if you donot have an account"}), 401
    
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        return jsonify({"Exception":str(traceback.extract_tb(exc_traceback))}), 500
    

@app.route('/signup', methods=['POST'])
def signup():
    try:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if(username and password and email):
            usr = db.user.find_one({"email":email})
            if(usr):
                return jsonify({'message':"User with email already exists"}), 401
            else:
                db.user.insert_one({"name":username,"email":email,"password":bcrypt.generate_password_hash(password).decode('utf-8')})
                return jsonify({'message':"Successfully Signed Up! You can now sign in!"}), 200
        else:
            return jsonify({'message':"Please enter valid details"}), 401
    
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        return jsonify({"Exception":str(traceback.extract_tb(exc_traceback))}), 500
    

@app.route('/bookTickets/<show_id>', methods=['POST'])
def bookTickets(show_id):
    try:
        show_id = ObjectId(show_id)
        
        if("user_id" in session):
            seat_numbers = eval(request.form["seat_numbers"])
            seat_type = request.form["seat_type"]
            
            if(show_id):
                for seat_no in seat_numbers:
                    db.seating.update_one({"show_id":show_id},{"$set":{"seats."+seat_type+"."+seat_no:1}})

                booking_id = (db.booking.insert_one({"user_id":ObjectId(session["user_id"]),"show_id":show_id,"seat_type":seat_type,"seat_numbers":seat_numbers})).inserted_id
                return jsonify({"message":"Seats Booked!!","booking_id":str(booking_id)}), 200
            else:
                return jsonify({"message":"Show not found"}), 404
        else:
            return jsonify({"message":"Please Login Before Booking Tickets"}), 401
    
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        return jsonify({"Exception":str(traceback.extract_tb(exc_traceback))}), 500


@app.route('/<city_name>/movies', methods=['GET'])
def getMoviesInCity(city_name):
    try:
        movies = []
        city_doc = db.city.find_one({"name":{ "$regex" : "^"+city_name+"$","$options" : "i"}})
        if(city_doc):
            for theatre in db.theatre.find({"city":{ "$regex" : "^"+city_name+"$","$options" : "i"}}):
                for mov_id in theatre["currently_playing"]:
                    movie = db.movie.find_one({"_id":mov_id})
                    if(movie not in movies):
                        movies.append(movie)
            if(movies):
                movies = json.loads(json_util.dumps(movies))
                return jsonify({"movies":movies}), 200
            else:
                return jsonify({"movies":None,"message":"No movies playing in the city"}), 200
        else:
            return jsonify({"message":"City not found"}), 404
    
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        return jsonify({"Exception":str(traceback.extract_tb(exc_traceback))}), 500



@app.route('/<city_name>/<movie_id>/theatres', methods=['POST'])
def getCityTheatresforMovie(city_name,movie_id):
    # Accept movie_id in the form of string

    try:
        date = request.form["date"] # Accept date in the form of string YYYY-MM-DD
        city_doc = db.city.find_one({"name":{ "$regex" : "^"+city_name+"$","$options" : "i"}})
        if(city_doc):
            theatres = []
            for theatre in db.theatre.find({"city":{ "$regex" : "^"+city_name+"$","$options" : "i"},"currently_playing":ObjectId(movie_id)},{"currently_playing":0}):
                shows = []
                for show in db.show.find({"theatre_id":theatre["_id"],"date":date},{"theatre_id":0,"movie_id":0}):
                    shows.append(show)
                if(shows):
                    theatre["shows"] = shows
                    theatres.append(theatre)
            
            if(theatres):
                theatres = json.loads(json_util.dumps(theatres))
                return jsonify({"theatres":theatres}), 200
            else:
                return jsonify({"theatres":None,"message":"No theatres found!"}), 200
        else:
            return jsonify({"message":"City not found"}), 404
    
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        return jsonify({"Exception":str(traceback.extract_tb(exc_traceback))}), 500



@app.route('/<show_id>/seats', methods=['POST'])    
def getSeatsAvailability(show_id):
    # type(show_id) = string
    try:
        seat_type = request.form["seat_type"]
        seats_need = int(request.form["seats_need"])
        show = db.show.find_one({"_id":ObjectId(show_id)})
        if(show):
            seats = db.seating.find_one({"show_id":ObjectId(show_id)})
            
            # LEFTOVER SEATS:
            available_seats = list(seats["seats"][seat_type].values())
            if(available_seats.count(0) >= seats_need):
                seats = json.loads(json_util.dumps(seats))
                return jsonify({"seats":seats}), 200
            else:
                return jsonify({"seats":None,"message":"No "+seat_type+" seats available!"}), 200    
        return jsonify({"message":"Show not found!"}), 404
    
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        return jsonify({"Exception":str(traceback.extract_tb(exc_traceback))}), 500
        
    


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
