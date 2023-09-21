import os, requests, json
from dotenv import load_dotenv
import base64

load_dotenv()

nemwman_runner_int_url = os.environ.get("NEWMAN_RUNNER_INT_URL")

def run_collection(postman_collection_id, postman_environment_id):
    run = requests.post(
        url = f"{nemwman_runner_int_url}/run/coll_id/{postman_collection_id}?{'env_id='+ postman_environment_id if postman_environment_id != '' else ''}"
    )
    return run.json()

def get_report(report_name):
    requested_report = requests.get(
        url = f"{nemwman_runner_int_url}/report?report_name={report_name}"
    )
    return requested_report.json()

def run_newman_and_get_report(postman_collection_id, postman_environment_id):
    run = run_collection(postman_collection_id, postman_environment_id)
    report = get_report(run["report_name"])
    return {"report_name": run['report_name'], "report": report}