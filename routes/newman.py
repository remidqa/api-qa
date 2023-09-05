from flask_restx import Namespace, Resource, fields, reqparse
from flask import request
import json
import urllib.request, urllib.parse, os
from dotenv import load_dotenv 
import requests

load_dotenv()

nemwman_runner_int_url = os.environ.get("NEWMAN_RUNNER_INT_URL")

api = Namespace('newman', description='Newman related operations')

@api.route("/run")
class runNewman(Resource):
    def post(self):
        coll_id = request.json["coll_id"]
        url = f"{nemwman_runner_int_url}/run/coll_id/{coll_id}"
        if ("env_id" in request.json.keys()):
            url+= f"?env_id={request.json['env_id']}"
        r = requests.post(url)
        return f"Status Code: {r.status_code}, Content: {r.json()}"
