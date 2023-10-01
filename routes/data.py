from flask_restx import Namespace, Resource
from dotenv import load_dotenv
import functions.mongodb as mongodb
from flask import request
import functions.utils as utils
from datetime import datetime

load_dotenv()

api = Namespace('run', description='Runs related operations')

@api.route("")
class run(Resource):
    def get(self):
        # DEFINE QUERY
        query = {}
        if request.args.get('app'):
            query['metadata.app'] = request.args.get('app')

        # DEFINE OPTIONS
        sort = {'value': request.args.get('sort').split(",")[0], 'direction': int(request.args.get('sort').split(",")[1])} if request.args.get('sort') else None
        limit = int(request.args.get('limit')) if request.args.get('limit') else 10
        documents = mongodb.find_documents('executions', query, {'sort': sort, 'limit': limit})

        analyse = {}

        for doc in documents:
            if doc['_id']: doc['_id'] = str(doc['_id'])
            app = doc['metadata']['app']
            testrun_title = doc['metadata']['testrun_title']
            if not analyse.get(app): analyse[app] = {}
            analyse[app][testrun_title] = {}
            if doc['executions']['newman']:
                details = {}
                for exec_name, exec_infos in doc['executions']['newman'].items():
                    run = exec_infos['report']['Run']
                    details[exec_name] = {
                        "assertions": {
                            'total': run['Stats']['Assertions']['total'],
                            'pending': run['Stats']['Assertions']['pending'],
                            'failed': run['Stats']['Assertions']['failed'],
                            'success': int(run['Stats']['Assertions']['total']) - int(run['Stats']['Assertions']['failed']) - int(run['Stats']['Assertions']['pending'])
                        },
                        'requests': {
                            'total': run['Stats']['Requests']['total'],
                            'pending': run['Stats']['Requests']['pending'],
                            'failed': run['Stats']['Requests']['failed'],
                            'success': int(run['Stats']['Requests']['total']) - int(run['Stats']['Requests']['pending']) - int(run['Stats']['Requests']['failed'])
                        },
                        'timings': {
                            'responseAverage': run['Timings']['responseAverage'],
                            'started': run['Timings']['started'],
                            'completed': run['Timings']['completed'],
                            'duration': int(run['Timings']['completed']) - int(run['Timings']['started'])
                        }
                    }
                summary = {
                    'assertions': {
                        'total': utils.dicts_sum(details, 'assertions.total'),
                        'pending': utils.dicts_sum(details, 'assertions.pending'),
                        'failed': utils.dicts_sum(details, 'assertions.failed'),
                        'success': utils.dicts_sum(details, 'assertions.success')
                    },
                    'requests': {
                        'total': utils.dicts_sum(details, 'requests.total'),
                        'pending': utils.dicts_sum(details, 'requests.pending'),
                        'failed': utils.dicts_sum(details, 'requests.failed'),
                        'success': utils.dicts_sum(details, 'requests.success')
                    },
                    'timings': {
                        'responseAverage': utils.dicts_sum(details, 'timings.responseAverage'),
                        'started': utils.dicts_sum(details, 'timings.started'),
                        'completed': utils.dicts_sum(details, 'timings.completed'),
                        'duration': utils.dicts_sum(details, 'timings.duration')
                    }
                    
                }
                analyse[app][testrun_title]['newman'] = {'details': details, 'summary': summary}
            else: analyse[app][testrun_title]['newman'] = None
            if doc['executions']['cypress']:
                details = {}
                for exec_name, exec_infos in doc['executions']['cypress'].items():

                    details[exec_name] = {
                        "tests": {
                            'total': exec_infos['report']['stats']['tests'],
                            'pending': exec_infos['report']['stats']['pending'],
                            'failed': exec_infos['report']['stats']['failures'],
                            'success': exec_infos['report']['stats']['passes']
                        },
                        'timings': {
                            'responseAverage': int(exec_infos['report']['stats']['duration'])/int(exec_infos['report']['stats']['tests']),
                            'started': datetime.fromisoformat(exec_infos['report']['stats']['start'].replace('Z', '+00:00')).timestamp(),
                            'completed': datetime.fromisoformat(exec_infos['report']['stats']['end'].replace('Z', '+00:00')).timestamp(),
                            'duration': int(datetime.fromisoformat(exec_infos['report']['stats']['end'].replace('Z', '+00:00')).timestamp())*1000 - int(datetime.fromisoformat(exec_infos['report']['stats']['start'].replace('Z', '+00:00')).timestamp())*1000
                        }
                    }
                summary = {
                    'tests': {
                        'total': utils.dicts_sum(details, 'tests.total'),
                        'pending': utils.dicts_sum(details, 'tests.pending'),
                        'failed': utils.dicts_sum(details, 'tests.failed'),
                        'success': utils.dicts_sum(details, 'tests.success')
                    },
                    'timings': {
                        'responseAverage': utils.dicts_sum(details, 'timings.responseAverage'),
                        'started': utils.dicts_sum(details, 'timings.started'),
                        'completed': utils.dicts_sum(details, 'timings.completed'),
                        'duration': utils.dicts_sum(details, 'timings.duration')
                    }
                }
                analyse[app][testrun_title]['cypress'] = {'details': details, 'summary': summary}
            else: analyse[app][testrun_title]['cypress'] = None
            summary = {
                'tests': {
                    'total': int(analyse[app][testrun_title]['newman']['summary']['assertions']['total']) if analyse[app][testrun_title]['newman'] else 0 + int(analyse[app][testrun_title]['cypress']['summary']['tests']['total']) if analyse[app][testrun_title]['cypress'] else 0,
                    'pending': int(analyse[app][testrun_title]['newman']['summary']['assertions']['pending']) if analyse[app][testrun_title]['newman'] else 0 + int(analyse[app][testrun_title]['cypress']['summary']['tests']['pending']) if analyse[app][testrun_title]['cypress'] else 0,
                    'failed': int(analyse[app][testrun_title]['newman']['summary']['assertions']['failed']) if analyse[app][testrun_title]['newman'] else 0+ int(analyse[app][testrun_title]['cypress']['summary']['tests']['failed']) if analyse[app][testrun_title]['cypress'] else 0,
                    'success': int(analyse[app][testrun_title]['newman']['summary']['assertions']['success']) if analyse[app][testrun_title]['newman'] else 0 + int(analyse[app][testrun_title]['cypress']['summary']['tests']['success']) if analyse[app][testrun_title]['cypress'] else 0
                },
                'timings': {
                    'duration': int(analyse[app][testrun_title]['newman']['summary']['timings']['duration']) if analyse[app][testrun_title]['newman'] else 0 + int(analyse[app][testrun_title]['cypress']['summary']['timings']['duration']) if analyse[app][testrun_title]['cypress'] else 0
                },
            }
            analyse[app][testrun_title]['summary'] = summary

            metadata = {
                'testiny.io_testrun_id': doc['metadata']['testiny.io_testrun_id'],
                'testiny.io_project_id': doc['metadata']['testiny.io_project_id']
            }
            analyse[app][testrun_title]['metadata'] = metadata
                


        return analyse