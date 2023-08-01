from flask import Flask

app = Flask(__name__)

# Import the routes module to register the routes with the app
import glocal_2.routes
