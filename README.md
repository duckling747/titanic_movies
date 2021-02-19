# Titanic Movies
It's a database-utilizing software project for the University of Helsinki course "Tietokantasovellus", 3rd period 2021. 
## What does it do?
It's a web app that let's you review movies, as long as the administrators have added them in. 
## Running it
The app uses docker heavily: presuming Linux or similar, run it in development mode by issuing `docker-compose up` from the command line inside the project root directory. This requires that you have a working installation of both docker and docker-compose. 
## Testing it
The app has some basic end-to-end tests written for it using Cypress. To run these tests, make sure you have the app running in development mode, using `docker-compose up`, and at the same time run the script `test_e2e.sh`, e.g. simply by issuing `./test_e2e.sh` inside the project's root directory.
## Just using it
The app has been deployed to Heroku as well. You can use it from there by navigating to the url [https://titanicmovies.herokuapp.com](https://titanicmovies.herokuapp.com).

