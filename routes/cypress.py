import requests, os
from flask_restx import Namespace, Resource
from flask import request
from dotenv import load_dotenv 
import functions.mongodb as mongodb
import functions.cy_runner as cy
import functions.testinyio as testinyio
import functions.github as git
import functions.utils as utils
#from functions.send_webhooks import send_webhook
import functions.discord as discord

load_dotenv()

api = Namespace('cypress_run', description='Cypress related operations')

def cypress_run(app, env, github_conf):
    # GET CONFIGURATION
    testinyio_project_id = github_conf['testinyio_project_id']
    scenarios = github_conf['scenarios']

    # RUN TESTS
    test_run = testinyio.create_testrun(app, env, testinyio_project_id)
    test_run_id = test_run['tr_id']
    executions = cy.run_cy_and_get_reports(app, env)
    testiny_updates = []
    for exec in executions:
        find_id = list(filter(lambda scenario: scenario["file_name"] == exec, scenarios))
        testinyio_testcase_id = find_id[0]['testinyio_testcase_id']
        testiny_update = testinyio.report_test_execution(test_run_id, testinyio_project_id, testinyio_testcase_id, executions[exec]['status'], executions[exec]['report'])
        testiny_updates.append(testiny_update)

    global_status = 'failure' if any(executions[exec]['status'] == "failure" for exec in executions) else 'success'

    inserted_report = mongodb.insert_document("cypress", executions)
    inserted_id = str(inserted_report.inserted_id)

    #webhook = send_webhook("cypress", inserted_id, global_status)
    webhook = discord.send_discord_webhook("cypress", inserted_id, global_status, app, env)
        
    return utils.send_json({
        "status": 200,
        "data": {
            "testiny_updates": testiny_updates,
            "cy_run_status": global_status,
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
        github_conf = git.get_cy_conf(app)

        response= cypress_run(app, env, github_conf)
        return response
