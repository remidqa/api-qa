import requests, os
from flask_restx import Namespace, Resource
from flask import request
from dotenv import load_dotenv 
import functions.mongodb as mongodb
import functions.cy_runner as cy
import functions.testinyio as testinyio
import functions.github as git
import functions.utils as utils
import functions.discord as discord

load_dotenv()

api = Namespace('cypress_run', description='Cypress related operations')

def cy_run(metadata, github_conf):
    # GET CONFIGURATION
    testinyio_project_id = github_conf['testinyio_project_id']
    scenarios = github_conf['scenarios']

    # RUN TESTS
    test_run_id = metadata["testiny.io_testrun_id"]
    executions = cy.run_cy_and_get_reports(metadata['app'], metadata['env'])
    testiny_updates = []
    for exec in executions:
        find_id = list(filter(lambda scenario: scenario["file_name"] == exec, scenarios))
        testinyio_testcase_id = find_id[0]['testinyio_testcase_id']
        testiny_update = testinyio.report_test_execution(test_run_id, testinyio_project_id, testinyio_testcase_id, executions[exec]['status'], executions[exec]['report'])
        testiny_updates.append(testiny_update)

    metadata['status'] =  'failure' if any(executions[exec]['status'] == "failure" for exec in executions) else 'success'

    inserted_report = mongodb.insert_document("cypress", metadata, executions)
    inserted_id = str(inserted_report.inserted_id)

    webhook = discord.send_discord_webhook("cypress", inserted_id, metadata['status'], metadata['app'], metadata['env'])
        
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
class runCypress(Resource):
    def post(self):
        # GET VARIABLES
        app = request.json["app"]
        env = request.json["env"]
        cy_conf = git.get_cy_conf(app, env)
        if cy_conf.get('err', {}):
            return cy_conf
        
        # GENERATE METADATA
        metadata = utils.generate_metadata(app, env, {"cy": cy_conf['scenarios']}, cy_conf['testinyio_project_id'])

        # Run tests
        response= cy_run(metadata, cy_conf)
        return response
