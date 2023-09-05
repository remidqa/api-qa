import json
from bson import json_util
from bson.objectid import ObjectId

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