import requests, os
from flask_restx import Namespace, Resource
from flask import request
from dotenv import load_dotenv 
import functions.cy_runner as cy
import functions.github as git
import routes.newman as newman
import routes.cypress as cy
import functions.utils as utils

load_dotenv()

api = Namespace('run', description='Runs related operations')

@api.route("")
class run(Resource):
    def post(self):
        # GET VARIABLES
        app = request.json["app"]
        env = request.json["env"]
        github_conf = git.get_full_conf(app, env)

        # GENERATE METADATA
        metadata = utils.generate_metadata(
            app,
            env, 
            {
                "newman": github_conf['newman']['scenarios'] if not github_conf['newman'].get('err') else None,
                "cy": github_conf['cy']['scenarios'] if not github_conf['cy'].get('err') else None
            },
            github_conf['testinyio_project_id']
        )

        request_newman = True if not github_conf.get('newman',{}).get('err', {}) else False
        request_cy = True if not github_conf.get('cy',{}).get('err', {}) else False

        newman_run = newman.run_newman(metadata, github_conf['newman']) if request_newman else None
        cy_run = cy.cy_run(metadata, github_conf['cy']) if request_cy else None

        newman_status = None if not request_newman else 'failure' if any(newman_run[f]['status'] == "failure" for f in newman_run) else 'success'
        cypress_status = None if not request_cy else 'failure' if any(cy_run[exec]['status'] == "failure" for exec in cy_run) else 'success'

        metadata['status'] = 'success' if (cypress_status == None or cypress_status == 'success' ) and (newman_status == None or newman_status == 'success' ) else 'failure'
        #metadata['status'] = 'failure' if newman_status == 'failure' or cypress_status == 'failure' else 'success'

        utils.post_results_and_webhook(metadata, {'cypress': cy_run, 'newman': newman_run})

        return {
            "metadata": metadata,
            "executions": {
                "newman": newman_run,
                "cypress": cy_run
            }
        }