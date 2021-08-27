# Installing Flask
* pip3 install Flask
* apt-get install python3-flask

# Running the application
1. Requirements must be installed in the environment - pip3 install -r requirements.txt
2. Following this tutorial - https://flask.palletsprojects.com/en/1.1.x/tutorial/factory/
Run next commands in console in the project path fbp-vs-soa/ride_allocation/soa_app_ml/
    * $ export FLASK_APP=flaskr
    * $ export FLASK_ENV=development
    * $ flask init-db
    * $ flask run
3. Run the main file of the fbp-vs-soa project passing "soa_app_ml" as a parameter