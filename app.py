from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scraping

# set up Flask
app = Flask(__name__)

# Tell Flask connect to PyMongo (Python MongoDB connection)
# Our Flask app will connect to Mongo using a Uniform Resource Identifier (url-like string) (URI)
app.config["MONGO_URI"] = 'mongodb://localhost:27017/mars_app'
mongo = PyMongo(app)

# Establish the root route
@app.route("/")
def index():
    # find the mars collection in the MongoDB and assign the path to variable mars
    mars = mongo.db.mars.find_one()
    # return the index.html file on our route, using the mars collection
    return render_template("index.html", mars=mars)

# Establish the scraping route
@app.route("/scrape")
def scrape():
    # assign a new variable mars that points to the MongoDB
    mars = mongo.db.mars
    # call the scrape_all() function from the scraping.py script, saving this to mars_data
    mars_data = scraping.scrape_all()
    # Data addition syntax: .update(query_parameter, data, options)
    # Add our scraped data to the MongoDB. Since this is new data, passing an empty JSON {} as the query_parameter, mars_data as the data, and upsert=True as options
    # upsert=True instructs MongoDB to create a new Document if it doesn't exist already
    mars.update({}, mars_data, upsert=True)
    # Redirect to the root route once the scrape is complete
    return redirect("/", code=302)

# Tell Flask to run the app
if __name__ == "__main__":
    app.run(debug=False)