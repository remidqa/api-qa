from flask_restx import Namespace, Resource, fields, reqparse
from flask import request
import json
import urllib.request, urllib.parse, os
from dotenv import load_dotenv 
import requests
import functions.mongodb as mongodb
import functions.utils as utils
import functions.github as git
import functions.testinyio as testinyio
import functions.newman_runner as newman
import functions.discord as discord

load_dotenv()

api = Namespace('newman', description='Newman related operations')

def run_newman(metadata, github_conf):
    # GET CONFIGURATION
    coll_id = github_conf['postman_collection_id']
    env_id = github_conf['postman_environment_id']
    testinyio_project_id = github_conf['testinyio_project_id']
    scenarios = github_conf['scenarios']

    # RUN COLLECTION
    executions = {}
    test_run_id = metadata["testiny.io_testrun_id"]
    for scenario in scenarios:
        scenario_name = scenario['folder_name']
        execution = newman.run_newman_and_get_report(coll_id, env_id, scenario_name)
        executions[scenario_name] = execution

        # SAVE EXECUTION IN TESTS MANAGEMENT TOOL
        tr = testinyio.report_test_execution(test_run_id, testinyio_project_id, scenario['testinyio_testcase_id'], execution['status'], execution['report'] )

    # SAVE EXECUTIONS IN DATABASE
    metadata['status'] = 'failure' if any(executions[f]['status'] == "failure" for f in executions) else 'success'
    inserted_report = mongodb.insert_document("newman", metadata, executions)
    inserted_id = str(inserted_report.inserted_id)


    # SLACK NOTIFICATION
    webhook = discord.send_discord_webhook("newman", inserted_id,  metadata['status'], metadata['app'], metadata['env'])
    
    return utils.send_json({
        "status": 200,
        "data": {
            "executions": executions,
            "status": metadata['status'],
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
        newman_conf = git.get_postman_conf(app, env)
        if newman_conf.get('err', {}):
            return newman_conf

        # GENERATE METADATA
        metadata = utils.generate_metadata(app, env, {"newman": newman_conf['scenarios']}, newman_conf['testinyio_project_id'])

        # Run tests
        response = run_newman(metadata, newman_conf)

        return response
