from flask_restx import Namespace, Resource, fields, reqparse
from flask import request
import json
import urllib.request, urllib.parse, os
from dotenv import load_dotenv 
import requests
from functions.send_webhooks import send_webhook
import functions.mongodb as mongodb
import functions.utils as utils
import functions.github as git
import functions.testinyio as testinyio
import functions.newman_runner as newman

load_dotenv()

nemwman_runner_int_url = os.environ.get("NEWMAN_RUNNER_INT_URL")

api = Namespace('newman', description='Newman related operations')

@api.route("/run")
class runNewman(Resource):
    def post(self):
        # GET VARIABLES
        app = request.json['app']
        env = request.json['env']

        # GET CONFIGURATION
        github_conf = git.get_postman_conf(app, env)
        coll_id = github_conf['postman_collection_id']
        env_id = github_conf['postman_environment_id']
        
        # RUN COLLECTION
        execution = newman.run_newman_and_get_report(coll_id, env_id)
        report_status = utils.get_report_status("newman", execution['report'])
        
        # SAVE EXECUTION IN TESTS MANAGEMENT TOOL
        tr = testinyio.report_test_execution( app, env, github_conf['testinyio_project_id'], github_conf['testinyio_testcase_id'], report_status, execution['report'] )
        
        # SAVE REPORT IN DATABASE
        inserted_report = mongodb.insert_document("newman", execution['report'])
        inserted_id = str(inserted_report.inserted_id)
        
        # DELETE REPORT IN NEWMAN RUNNER
        deleted_report = requests.delete(f"{nemwman_runner_int_url}/report?report_name={execution['report_name']}")

        # SLACK NOTIFICATION
        webhook = send_webhook("newman", inserted_id, report_status)
        
        
        return utils.send_json({
            "status": 200,
            "data": {
                "tr": tr,
                "newman_run": execution,
                "inserted_id_in_mongodb": inserted_id,
                "webhook": webhook
            }
        })