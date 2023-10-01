import json
from bson import json_util
from bson.objectid import ObjectId
from datetime import datetime
import pytz, time
import functions.testinyio as testinyio
import functions.discord as discord
import functions.mongodb as mongodb

def get_report_status(runner, report):
    report_status = False
    if runner == "newman":
        report_status = "failure" if len(report["Run"]["Failures"]) != 0 else "success"
    elif runner == "cypress":
        report_status = "failure" if report["stats"]["failures"] != 0 else "success"
    return report_status

def send_json(json_object):
    return json.loads(json_util.dumps(json_object))

def check_query(body):
    query = {}
    if (body) and (isinstance(body, dict)) and ("query" in body.keys()) and (isinstance(body["query"], dict)):
        query = body["query"]
        if query["_id"]:
            id = query["_id"]
            query["_id"] = ObjectId(id)
    return query

def generate_testrun_title(timestamp):
    dt = datetime.fromtimestamp(timestamp)
    ca_east_tz = pytz.timezone('America/Montreal')
    dt_ca = dt.astimezone(ca_east_tz)
    year = dt_ca.year
    month = str(dt_ca.month).zfill(2)
    day = str(dt_ca.day).zfill(2)
    week_day = dt_ca.strftime('%A')[:3]
    hour = str(dt_ca.hour).zfill(2)
    minute = str(dt_ca.minute).zfill(2)
    second = str(dt_ca.second).zfill(2)
    ms = str(dt_ca.microsecond).zfill(6)[:2]
    
    return f"{year}_{month}_{day}-{week_day}-{hour}:{minute}:{second}.{ms}"

def get_tests_list(list, runner):
    return [''.join(d.values()) for d in [{k: v for k, v in d.items() if k != 'testinyio_testcase_id'} for d in list[runner]]]

def generate_metadata(app, env, scenarios, testinyio_project_id):
    ts = time.time()
    tests_list = {
        "newman": get_tests_list(scenarios, 'newman') if scenarios.get('newman', {}) else [],
        "cy": get_tests_list(scenarios, 'cy') if scenarios.get('cy', {}) else []
    }
    testrun_title= f"{app}_{env}_{generate_testrun_title(ts)}"
    return {
        "tests_list": tests_list,
        "req_timestamp": ts,
        "app": app,
        "env": env,
        "testrun_title": testrun_title,
        "testiny.io_project_id": testinyio_project_id,
        "testiny.io_testrun_id": testinyio.create_testrun(testrun_title, testinyio_project_id)
    }

def post_results_and_webhook(metadata, executions):
    # CHECK EXECUTIONS
    if not executions.get("newman"):
        executions['newman'] = None
    if not executions.get("cypress"):
        executions['cypress'] = None

    inserted_report = mongodb.insert_document("executions", {'metadata': metadata, 'executions':executions})
    inserted_id = str(inserted_report.inserted_id)

    # SLACK NOTIFICATION
    webhook = discord.send_discord_webhook(inserted_id,  metadata['status'], metadata['app'], metadata['env'])
    
    return send_json({
        "status": 200,
        "data": {
            "executions": executions,
            "status": metadata['status'],
            "inserted_id_in_mongodb": inserted_id,
            "webhook": webhook
        }
    })

def dicts_sum(dictionary, key):
    sum = 0
    keys = key.split('.')
    for i_name, d_value in dictionary.items():
        temp = d_value
        for k in keys:
            temp = temp[k]
        sum += int(temp)
    return sum

