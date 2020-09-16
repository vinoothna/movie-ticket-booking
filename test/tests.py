############# IMPORTS #############

import json
import os, sys
sys.path.append('../')

from datetime import datetime
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from flask import Flask, jsonify, request, session
from pymongo import MongoClient
from pymongo.errors import OperationFailure, ConfigurationError
from bson import json_util, ObjectId

import pytest
from api import app as flask_app




#####  FIXTURES: Also referred to as dependency injections #####

@pytest.fixture
def app():
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()



@pytest.mark.order1
def test_index(app, client):
    res = client.get('/')
    assert res.status_code == 200


@pytest.mark.order2
def test_page_not_found(app, client):
    res = client.get('/home')
    assert res.status_code == 404


@pytest.mark.order7
def test_signup(app, client):

    # NEW USER
    payload = {
        "username": os.getenv("TEST_USERNAME"),
        "email" : os.getenv("TEST_EMAIL"),
        "password" : os.getenv("TEST_PASSWORD")
    }
    res = client.post('/signup', data=payload )
    assert res.status_code == 200

    # EXISTING USER CANNOT SIGNUP
    res = client.post('/signup', data=payload )
    assert res.status_code == 401


    # REQUEST WITH NO PAYLOAD IS INVALID
    res = client.post('/signup')
    assert res.status_code == 500
    print(res.get_json())


@pytest.mark.order8
def test_login(app, client):
    payload = {
        "email" : os.getenv("TEST_EMAIL"),
        "password" : os.getenv("TEST_PASSWORD")
    }
    res = client.post('/login', data=payload )
    assert res.status_code == 200


@pytest.mark.order9
def test_logout(app,client):
    res = client.post("/logout")
    res.status_code == 200

@pytest.mark.order3
def test_dbConnection():
    try:
        client = MongoClient(os.getenv("MONGO_URL"))
        client.admin.command('ismaster')
        assert True
    except Exception as e: ## None of DNS query names exist, Connection Failures
        #print("Exception =",str(e))
        assert False


@pytest.mark.order4
def test_getMoviesInCity(app, client):
    # VALID REQUEST
    res = client.get('/Hyderabad/movies')
    assert res.status_code == 200
    
    # INVALID CITY NAME
    res = client.get('/XYZ/movies')
    assert res.status_code == 404

    # CASE INSENSITIVE SEARCH SHOULD WORK
    res = client.get('/HYderabAD/movies')
    assert res.status_code == 200


@pytest.mark.order5
def test_getTheatresforMovie(app, client):
    # NO PAYLOAD SHOULD THROW AN ERROR
    res = client.post('/Hyderabad/5f5e2a973d8397211b9dbbde/theatres')
    assert res.status_code == 500

    # VALID DETALS
    res = client.post('/Hyderabad/5f5f1891651ffce851fc231c/theatres',data={"date":"2020-09-20"})
    assert res.status_code == 200


    # NOT A RECENT MOVIE
    res = client.post('/Hyderabad/5f5e2a973d8397211b9dbbde/theatres',data={"date":"2020-09-20"})
    assert res.status_code == 200
    result_data = res.get_json()
    assert result_data["theatres"] == None
    assert result_data["message"] == "No theatres found!"
    
    # INVALID LOCATION
    res = client.post('/XYZ/5f5e2a973d8397211b9dbbde/theatres',data={"date":"2020-09-20"})
    assert res.status_code == 404
    

@pytest.mark.order6
def test_getSeatsAvailability(app,client):

    ## INVALID SEATS_NEED (Cannot be fulfilled)
    payload = {
        "seat_type":"lounge",
        "seats_need":100
    }
    res = client.post("/5f5f9f895627e28fe5de099e/seats",data=payload)
    assert res.status_code == 200
    result_data = res.get_json()
    assert result_data["seats"] == None

    # VALID DETAILS
    payload = {
        "seat_type":"lounge",
        "seats_need":10
    }
    res = client.post("/5f5f9f895627e28fe5de099e/seats",data=payload)
    assert res.status_code == 200
    result_data = res.get_json()
    assert result_data["seats"] != None

    ## show_id not found
    payload = {
        "seat_type":"lounge",
        "seats_need":10
    }
    res = client.post("/5f62085044301d2b7dafef9b/seats",data=payload)
    assert res.status_code == 404

    # INVALID REQUEST
    res = client.post("/5f62085044301d2b7dafef/seats")
    assert res.status_code == 500




@pytest.mark.order10
def test_bookTickets(app,client):

    # CANNOT BOOK TICKETS WITHOUT LOGGING IN
    payload = {
        "seat_numbers":'["A4","A5","A6"]',
        "seat_type":"dress_circle"
    }
    res = client.post("/bookTickets/5f5f9f895627e28fe5de099e", data=payload)
    res.status_code == 401
    result = res.get_json()
    assert result["message"] == "Please Login Before Booking Tickets"

    payload = {
        "email" : os.getenv("TEST_EMAIL"),
        "password" : os.getenv("TEST_PASSWORD")
    }
    res = client.post('/login', data=payload )
    assert res.status_code == 200


    payload = {
        "seat_numbers":"['A4','A5','A6']",
        "seat_type":"dress_circle"
    }
    res = client.post("/bookTickets/5f5f9f895627e28fe5de099e", data=payload)
    res.status_code == 200
    result = res.get_json()
    assert result["message"] == "Seats Booked!!"



    