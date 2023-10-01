from flask_restx import Namespace, Resource
from dotenv import load_dotenv
import functions.mongodb as mongodb
from flask import request
import functions.utils as utils
from datetime import datetime

load_dotenv()

api = Namespace('run', description='Runs related operations')

def convert_date_to_timestamp(date_string):
    date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    dt = datetime.strptime(date_string, date_format)
    timestamp = round(dt.timestamp() * 1000)
    return timestamp

def sum(data, query):
    keys = query.split('.')
    result = 0
    for i in list(data.keys()):
        temp = data[i]
        for k in keys:
            temp = temp[k]
        result = result + int(temp)
    return result

def avg(data, query):
    keys = query.split('.')
    result = 0
    for i in list(data.keys()):
        temp = data[i]
        for k in keys:
            temp = temp[k]
        result = result + int(temp)
    return  round(result / len(list(data.keys())), 2)

def generate_scenario_metrics(type, scenario_metrics):
    test_metrics = scenario_metrics['report']['Run']['Stats']['Assertions'] if type == 'newman' else scenario_metrics['report']['stats'] if type == 'cypress' else None
    timings_metrics = scenario_metrics['report']['Run']['Timings'] if type == 'newman' else scenario_metrics['report']['stats'] if type == 'cypress' else None
    temp = {
        "tests": {
            "total": int(test_metrics['total']) if type == 'newman' else int(test_metrics['tests']) if type == 'cypress' else 0,
            "pending": int(test_metrics['pending']) if type == 'newman' or type == 'cypress' else 0,
            "failed": int(test_metrics['failed']) if type == 'newman' else int(test_metrics['failures']) if type == 'cypress' else 0,
            #"success": (int(test_metrics['total']) - int(test_metrics['pending']) - int(test_metrics['failed'])) if type == 'newman' else ((int(test_metrics['tests']) - int(test_metrics['pending']) - int(test_metrics['failures'])) if type == 'cypress' else 0)
        },
        "timings": {
            "responseAverage": int(timings_metrics['responseAverage']) if type == 'newman' else int(int(timings_metrics['duration']) / int(timings_metrics['tests'])/10) if type == 'cypress' else 0,
            "started": int(timings_metrics['started']) if type == 'newman' else int(convert_date_to_timestamp(timings_metrics['start'])) if type == 'cypress' else 0,
            "completed": int(timings_metrics['completed']) if type == 'newman' else int(convert_date_to_timestamp(timings_metrics['end'])) if type == 'cypress' else 0,
            "duration": (int(timings_metrics['completed']) - int(timings_metrics['started'])) if type == 'newman' else ((int(convert_date_to_timestamp(timings_metrics['end'])) - int(convert_date_to_timestamp(timings_metrics['start']))) if type == 'cypress' else 0)
        }
    }
    temp['tests']['success'] = int(temp['tests']['total']) - int(temp['tests']['pending']) - int(temp['tests']['failed'])
    temp['tests']['status'] = 'success' if temp['tests']['total'] == temp['tests']['success'] else 'failed'
    return temp

def sum_status(scenarios_details):
    count_total = 0
    count_success = 0
    count_failed = 0
    for scenario in scenarios_details:
        count_total = count_total + 1
        if scenarios_details[scenario]['tests']['status'] == 'success': count_success = count_success + 1
        if scenarios_details[scenario]['tests']['status'] == 'failed': count_failed = count_failed + 1
    return {
        'total': count_total,
        'failed': count_failed,
        'success': count_success
    }
        

def generate_scenarios_summary(scenarios_details):
    return {
        "tests": sum_status(scenarios_details),
        "timings": {
            "responseAverage": avg(scenarios_details, 'timings.responseAverage'),
            "duration": sum(scenarios_details, "timings.duration")
        }
    }

def generate_scenarios_metrics(type, executions):
    scenarios = list(executions.keys())
    details = {}
    for scenario in scenarios:
        details[scenario] = generate_scenario_metrics(type, executions[scenario])
    summary = generate_scenarios_summary(details)
    return {'details': details, 'summary': summary}

def generate_summary(newman_summary, cypress_summary):
    newman_avg = newman_summary['timings']['responseAverage'] if newman_summary else 0
    cypress_avg = cypress_summary['timings']['responseAverage'] if cypress_summary else 0
    count = 1
    if newman_summary and cypress_summary: count = count +1
    summary_responseAverage =  (newman_avg + cypress_avg) / count
    return {
        "tests": {
            "total": (newman_summary['tests']['total'] if newman_summary else 0) + (cypress_summary['tests']['total'] if cypress_summary else 0),
            #"pending": (newman_summary['tests']['pending'] if newman_summary else 0) + (cypress_summary['tests']['pending'] if cypress_summary else 0),
            "failed": (newman_summary['tests']['failed'] if newman_summary else 0) + (cypress_summary['tests']['failed'] if cypress_summary else 0),
            "success": (newman_summary['tests']['success'] if newman_summary else 0) + (cypress_summary['tests']['success'] if cypress_summary else 0)
        },
        "timings": {
            "responseAverage": summary_responseAverage,
            "duration": (newman_summary['timings']['duration'] if newman_summary else 0) + (cypress_summary['timings']['duration'] if cypress_summary else 0)
        }
    }

def generate_metadata(metadata):
    return {
        "testiny.io_testrun_id": metadata['testiny.io_testrun_id'],
        "testiny.io_project_id": metadata['testiny.io_project_id']
    }

def find_report(documents, app, report_name):
    report = {}
    for doc in documents:
        if doc['metadata']['app'] == app and doc['metadata']['testrun_title'] == report_name: report = doc
    return report

def generate_metrics(documents, dataset):
    metrics = {}
    for app in list(dataset.keys()):
        metrics[app] = {}
        for report_name in list(dataset[app].keys()):
            tests_list = dataset[app][report_name]
            mongo_report = find_report(documents, app, report_name)
            report_metrics = {}
            newman_executed = True if len(tests_list['newman']) > 0 else False
            cypress_executed = True if len(tests_list['cypress']) > 0 else False

            report_metrics['newman'] = generate_scenarios_metrics('newman', mongo_report['executions']['newman']) if newman_executed else None
            report_metrics['cypress'] = generate_scenarios_metrics('cypress', mongo_report['executions']['cypress']) if cypress_executed else None
            report_metrics['summary'] = generate_summary(report_metrics['newman']['summary'] if newman_executed else None, report_metrics['cypress']['summary'] if cypress_executed else None)
            report_metrics['metadata'] = generate_metadata(mongo_report['metadata'])
            if report_name == 'full-stack_uat_2023_10_01-Sun-15:53:17.86': print(report_metrics['summary'])

            metrics[app][report_name] = report_metrics

    return metrics

template = {
        '__app__': {
            '__report_name__': {
                'newman': {
                    'details': {
                        '__scenario_name__': {
                            "assertions": {
                                "total": 0,
                                "pending": 0,
                                "failed": 0,
                                "success": 0
                            },
                            "requests": {
                                "total": 0,
                                "pending": 0,
                                "failed": 0,
                                "success": 0
                            },
                            "timings": {
                                "responseAverage": 0,
                                "started": 0,
                                "completed": 0,
                                "duration": 0
                            }
                        }
                    },
                    'summary':  {
                        "tests": {
                            "total": 0,
                            "pending": 0,
                            "failed": 0,
                            "success": 0
                        },
                        "timings": {
                            "responseAverage": 0,
                            "duration": 0
                        }
                    }
                },
                'cypress': {
                    'details': {
                        '__scenario_name__': {
                            "tests": {
                                "total": 0,
                                "pending": 0,
                                "failed": 0,
                                "success": 0
                            },
                            "timings": {
                                "responseAverage": 0,
                                "started": 0,
                                "completed": 0,
                                "duration": 0
                            }
                        }
                    },
                    'summary':  {
                        "tests": {
                            "total": 0,
                            "pending": 0,
                            "failed": 0,
                            "success": 0
                        },
                        "timings": {
                            "responseAverage": 0,
                            "duration": 0
                        }
                    }
                },
                'summary': {
                    "tests": {
                        "total": 0,
                        "pending": 0,
                        "failed": 0,
                        "success": 0
                    },
                    "timings": {
                        "responseAverage": 0,
                        "duration": 0
                    }
                },
                "metadata": {
                    "testiny.io_testrun_id": 0,
                    "testiny.io_project_id": 0
                }   
            }
        }
    }


@api.route("")
class run(Resource):
    def get(self):
        # DEFINE QUERY
        query = {}
        if request.args.get('app'):
            query['metadata.app'] = request.args.get('app')

        # DEFINE OPTIONS
        #sort = {'value': request.args.get('sort').split(",")[0], 'direction': int(request.args.get('sort').split(",")[1])} if request.args.get('sort') else None
        #limit = int(request.args.get('limit')) if request.args.get('limit') else 10
        documents = mongodb.find_documents('executions', query, {'sort': {'value': 'metadata.req_timestamp', 'direction': -1}, 'limit': 100})
        
        #for doc in documents:
        #    if doc['_id']: del doc['_id']
        #return documents

        dataset = {}
        #dataset_example = {'front-qa':{'report_name':{'newman':[], 'cypress':[]}}}

        for doc in documents:
            if doc['_id']: del doc['_id']
            app = doc['metadata']['app']
            testrun_title = doc['metadata']['testrun_title']
            newman_tests_list = doc['metadata']['tests_list']['newman'] if doc['metadata']['tests_list'].get('newman') else []
            cypress_tests_list = doc['metadata']['tests_list']['cy'] if doc['metadata']['tests_list'].get('cy') else []
            if not any(value == app for value in list(dataset.keys())): dataset[app]={}
            if not any(value == testrun_title for value in list(dataset[app].keys())): dataset[app][testrun_title]={
                'newman': newman_tests_list,
                'cypress': cypress_tests_list
            }
        #return dataset
        analyse = generate_metrics(documents, dataset)


        return analyse