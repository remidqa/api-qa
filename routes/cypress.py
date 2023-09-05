import requests, os
from flask_restx import Namespace, Resource
from flask import request
from dotenv import load_dotenv 
import functions.mongodb as mongodb
import functions.utils as utils
from functions.send_webhooks import send_webhook

load_dotenv()

cy_runner_int_url = os.environ.get("CY_RUNNER_INT_URL")

api = Namespace('cypress_run', description='Cypress related operations')

@api.route("/run")
class runCypress(Resource):
    def post(self):
        app = request.json["app"]
        run = requests.post(f"{cy_runner_int_url}/run/app/{app}")
        report_name = run.json()["infos"]["reportName"]
        requested_report = requests.get(f"{cy_runner_int_url}/report/report_name/{report_name}")
        report = requested_report.json()
        inserted_report = mongodb.insert_document("cypress", report)
        inserted_id = str(inserted_report.inserted_id)
        deleted_report = requests.delete(f"{cy_runner_int_url}/report/report_name/{report_name}")
        deleted_msg = deleted_report.json()["msg"]
        report_status = utils.get_report_status("cypress", report)
        webhook = send_webhook("cypress", inserted_id, report_status)
        return utils.send_json({
            "status": 200,
            "data": {
                "cy_run": run.json(),
                "requested_report": requested_report.json(),
                "inserted_id_in_mongodb": inserted_id,
                "webhook": webhook
            }
        })