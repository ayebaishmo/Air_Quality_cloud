from flask import Flask
from air_quality import openaq

def create_app():

    app = Flask(__name__)

    api = openaq.OpenAQ
    status, resp = api.measurements(city = 'Delhi')

    @app.route('/')
    def root():
        """Base view"""
        return status
    
    return app