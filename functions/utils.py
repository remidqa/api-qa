import json
from bson import json_util
from bson.objectid import ObjectId
from datetime import datetime
import pytz



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

def generate_report_name():
    dt = datetime.now()
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