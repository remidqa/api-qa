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
import functions.discord as discord

load_dotenv()

api = Namespace('newman', description='Newman related operations')

def run_newman(app, env, github_conf):
    # GET CONFIGURATION
    coll_id = github_conf['postman_collection_id']
    env_id = github_conf['postman_environment_id']
    testinyio_project_id = github_conf['testinyio_project_id']
    folders = github_conf['folders']
        
    # RUN COLLECTION
    reports = {}
    test_run = testinyio.create_testrun(app, env, testinyio_project_id)
    test_run_id = test_run['tr_id']
    for folder in folders:
        folder_name = folder['folder_name']
        execution = newman.run_newman_and_get_report(coll_id, env_id, folder_name)
        reports[folder_name] = execution

        # SAVE EXECUTION IN TESTS MANAGEMENT TOOL
        tr = testinyio.report_test_execution(test_run_id, testinyio_project_id, folder['testinyio_testcase_id'], execution['status'], execution['report'] )

    # SAVE EXECUTIONS IN DATABASE
    global_status = 'failure' if any(reports[f]['status'] == "failure" for f in reports) else 'success'
    inserted_report = mongodb.insert_document("newman", reports)
    inserted_id = str(inserted_report.inserted_id)


    # SLACK NOTIFICATION
    webhook = discord.send_discord_webhook("newman", inserted_id, global_status, app, env)
    #webhook = send_webhook("newman", inserted_id, global_status)
    
    return utils.send_json({
        "status": 200,
        "data": {
            "tr": tr,
            "newman_run": execution,
            "inserted_id_in_mongodb": inserted_id,
            "webhook": webhook
        }
    })

@api.route("/run")
class runNewman(Resource):
    def post(self):
        # GET VARIABLES
        app = request.json['app']
        env = request.json['env']
        github_conf = git.get_postman_conf(app, env)

        response = run_newman(app, env, github_conf)

        return response