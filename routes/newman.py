from flask_restx import Namespace, Resource, fields, reqparse
from flask import request
import json
import urllib.request, urllib.parse, os
from dotenv import load_dotenv 
import requests
from functions.send_webhooks import send_webhook
import functions.mongodb as mongodb
import functions.utils as utils


load_dotenv()

nemwman_runner_int_url = os.environ.get("NEWMAN_RUNNER_INT_URL")

api = Namespace('newman', description='Newman related operations')

@api.route("/run")
class runNewman(Resource):
    def post(self):
        coll_id = request.json["coll_id"]
        env_id = request.json["env_id"] if "env_id" in request.json else ""
        run = requests.post(f"{nemwman_runner_int_url}/run/coll_id/{coll_id}?{'env_id='+env_id if env_id != '' else ''}")
        report_name = run.json()["report_name"]
        requested_report = requests.get(f"{nemwman_runner_int_url}/report?report_name={report_name}")
        report = requested_report.json()
        inserted_report = mongodb.insert_document("newman", report)
        inserted_id = str(inserted_report.inserted_id)
        deleted_report = requests.delete(f"{nemwman_runner_int_url}/report?report_name={report_name}")
        deleted_msg = deleted_report.json()["msg"]
        report_status = utils.get_report_status("newman", report)
        webhook = send_webhook("newman", inserted_id, report_status)
        return utils.send_json({
            "status": 200,
            "data": {
                "newman_run": run.json(),
                "requested_report": requested_report.json(),
                "inserted_id_in_mongodb": inserted_id,
                "webhook": webhook
            }
        })
    #def post(self):
    #    coll_id = request.json["coll_id"]
    #    url = f"{nemwman_runner_int_url}/run/coll_id/{coll_id}"
    #    if ("env_id" in request.json.keys()):
    #        url+= f"?env_id={request.json['env_id']}"
    #    r = requests.post(url)
    #    return f"Status Code: {r.status_code}, Content: {r.json()}"
