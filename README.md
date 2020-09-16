<!-- PROJECT LOGO -->
<br />
<p align="center">

  <h1 align="center">MOVIE TICKET BOOKING SYSTEM BACKEND</h1>

  <p align="center">
    Backend APIs for the movie ticket booking system
    <br />
  </p>
</p>


<br><br>
<!-- ABOUT THE PROJECT -->
## About The Project

**Current Features:**

APIs with:
- Ability to view all the movies playing in your city
- Ability to check all cinemas in which a movie is playing along with all the showtimes
- Ability to check the availability of seats for each showtime
- User Sign up and login 
- Ability to book a ticket only on login (No payment gateway integration is currently setup. Assuming tickets can be booked for free)

*The Database Design and other stuff is explained in the pdf in the documentation directory of the project (any mistakes can be rectified in the contributions)*


### Built With
* [Flask](https://flask.palletsprojects.com/en/1.1.x/)
* [MongoDB](https://www.mongodb.com/)



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

* Python 3.6+
* pip
* MongoDB account

### Installation


1. Clone the repo
```sh
git clone https://github.com/vinoothna/movie-ticket-booking.git
```
2. Install requirements using pip
```sh
pip install -r requirements.txt
```
3. Initially, create a .env file in the root directory with

```sh
MONGO_URL=PUT MONGO CONNECTION SRV STRING HERE
SECRET_KEY=SOME RANDOM SECRET KEY
TEST_USERNAME=testusername
TEST_EMAIL=test_email@gmail.com
TEST_PASSWORD=testPassword
```
4. Create a db called `bookyshow`. Database can be pupulated using all the code in the Jupyter Notebook and CSV files provided.



<!-- USAGE EXAMPLES -->
## How to run?
Just run
```sh
python3 app.py
```
The API usage is described in detail in this documentation: https://explore.postman.com/templates/12552/caw-studios-assignment---bookmyshow-backend


## How to test?

To execute the unit tests, go to **test folder** and run
```sh
pytest tests.py
```



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



<!-- CONTACT -->
## Contact

Vinoothna Sai K - vinoothna.kinnera@gmail.com

Project Link: [https://github.com/vinoothna/movie-ticket-booking/](https://github.com/vinoothna/movie-ticket-booking/)



