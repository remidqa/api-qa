from flask_restx import Namespace, Resource, fields, reqparse
from flask import request
import json
import urllib.request, urllib.parse, os
from dotenv import load_dotenv 
import requests

load_dotenv()

cy_runner_int_url = os.environ.get("CY_RUNNER_INT_URL")

api = Namespace('cypress_run', description='Cypress related operations')

@api.route("/run")
class runCypress(Resource):
    def post(self):
        app = request.json["app"]
        r = requests.post(f"{cy_runner_int_url}/run/app/{app}")
        return f"Status Code: {r.status_code}, Content: {r.json()}"
