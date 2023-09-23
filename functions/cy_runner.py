import os, requests, json
from dotenv import load_dotenv
import base64, re
import functions.utils as utils

load_dotenv()

cy_runner_int_url = os.environ.get("CY_RUNNER_INT_URL")

def run_tests(app, env):
    run = requests.post(
        url = f"{cy_runner_int_url}/run",
        json = {
            "app": app,
            "env": env   
        }
    )
    return run.json()

def get_report(folder, report_name):
    requested_report = requests.get(
        url = f"{cy_runner_int_url}/report/folder/{folder}/report_name/{report_name}"
    )
    return requested_report.json()

def delete_report(folder, report_name):
    requests.delete(
        url = f"{cy_runner_int_url}/report/folder/{folder}/report_name/{report_name}"
    )

def run_cy_and_get_reports(app, env):
    executions = {}
    run = run_tests(app, env)

    for report_name in run['infos']['reports']:
        report = get_report(run['infos']['reportsFolder'], report_name)
        regex = re.match(r"(\w+)_(.+)-report", report_name)
        cy_status = regex.group(1)
        test_name = regex.group(2)
        status = 'success' if cy_status == 'pass' else 'failure'
        executions[test_name] = {"status": status, "report": report}
        #executions.append({"status": status, "test_name": test_name, "report": report})
        delete_report(run['infos']['reportsFolder'], report_name)

    return executions