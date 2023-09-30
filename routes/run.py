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

        newman_run = newman.run_newman(metadata, github_conf['newman']) if not github_conf.get('newman',{}).get('err', {}) else github_conf['newman']['err']
        cy_run = cy.cy_run(metadata, github_conf['cy']) if not github_conf.get('cy',{}).get('err', {}) else github_conf['cy']['err']
        return {
            "newman": newman_run,
            "cypress": cy_run
        }