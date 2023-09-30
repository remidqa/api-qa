import os, requests, json
from dotenv import load_dotenv
import base64
import functions.utils as utils

load_dotenv()

nemwman_runner_int_url = os.environ.get("NEWMAN_RUNNER_INT_URL")

def run_collection(postman_collection_id, postman_environment_id, scenario_name):
    run = requests.post(
        url = f"{nemwman_runner_int_url}/run",
        json = {
            "coll_id": postman_collection_id,
            "env_id": postman_environment_id,
            "folder": scenario_name
        }
    )
    return run.json()

def get_report(report_name):
    requested_report = requests.get(
        url = f"{nemwman_runner_int_url}/report?report_name={report_name}"
    )
    return requested_report.json()

def delete_report(report_name):
    requests.delete(
        url = f"{nemwman_runner_int_url}/report?report_name={report_name}"
    )

def run_newman_and_get_report(postman_collection_id, postman_environment_id, scenario_name):
    run = run_collection(postman_collection_id, postman_environment_id, scenario_name)
    report = get_report(run["report_name"])
    report_status = utils.get_report_status("newman", report)
    delete_report(run["report_name"])
    return {
        "report_name": run['report_name'],
        "status": report_status,
        "report": report
    }