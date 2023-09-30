import os, requests, json
from dotenv import load_dotenv
import base64
import functions.utils as utils

load_dotenv()

testinyio_url = os.environ.get("TESTINYIO_URL")
testinyio_token = os.environ.get("TESTINYIO_TOKEN")

def create_testrun(testrun_title, project_id):
    tr_creation = requests.post(
    url = f'{testinyio_url}/testrun',
    headers = { 'X-Api-Key': testinyio_token },
    json = {
        'project_id': project_id,
        'title': testrun_title
    }
    )
    data= tr_creation.json()
    return data['id']

def add_tc_to_tr(tr_id, tc_id, status):
    adding_tc_to_tr = requests.post(
        url = f'{testinyio_url}/testrun/mapping/bulk/testcase:testrun?op=add',
        headers = { 'X-Api-Key': testinyio_token },
        json = [
            {
                "ids": {
                    "testcase_id": tc_id,
                    "testrun_id": tr_id
                },
                "mapped": {
                    "assigned_to": "OWNER",
                    "result_status": f"{'PASSED' if status == 'success' else 'FAILED'}"
                }
            }
        ]
    )
    return adding_tc_to_tr.status_code

def create_attachment(report, project_id):
    report_dump = json.dumps(report)
    report_base64_encoded = base64.encodebytes(report_dump.encode())
    created_attachment = requests.post(
        url = f'{testinyio_url}/blob',
        headers = { 'X-Api-Key': testinyio_token },
        json = {
            "project_id": project_id,
            "mime_type": "text/plain",
            "filename": "report.json",
            "data": report_base64_encoded.decode()
        }
    )
    json_resp = created_attachment.json()
    response = {
        "id": json_resp['id'],
        "blob_id": json_resp['blob_id'],
        "size": json_resp['size']
    }
    return response

def create_comment(project_id, attachment_id, blob_id, size):
    created_attachment = requests.post(
        url = f'{testinyio_url}/comment',
        headers = { 'X-Api-Key': testinyio_token },
        json = {
            "project_id": project_id,
            "status": "OPEN",
            "type": "ATTACHMENT",
            "text": f"{attachment_id}|{blob_id}||report.json|text/plain|{size}"
        }
    )
    json_resp = created_attachment.json()
    return {'id': json_resp['id'] }

def link_comment_to_tr(tr_id, tc_id, comment_id):
    linked_comment = requests.post(
        url = f'{testinyio_url}/comment/mapping/bulk/comment:testcase:testrun?op=add',
        headers = { 'X-Api-Key': testinyio_token },
        json = [
            {
                "ids": {
                    "comment_id": comment_id,
                    "testcase_id": tc_id,
                    "testrun_id": tr_id
                }
            }
        ]
    )
    return {'status_code': linked_comment.status_code, 'data': linked_comment.json(), 'req': [
            {
                "ids": {
                    "comment_id": comment_id,
                    "testcase_id": tc_id,
                    "testrun_id": tr_id
                }
            }
        ]}

def link_attachment_to_comment(attachment_id, comment_id):
    linked_attachment = requests.post(
        url = f'{testinyio_url}/blob/mapping/bulk/blob:comment?op=add',
        headers = { 'X-Api-Key': testinyio_token },
        json = [
            {
                "ids": {
                    "blob_id": attachment_id,
                    "comment_id": comment_id
                }
            }
        ]
    )
    return {'status_code': linked_attachment.status_code, 'data': linked_attachment.json(), "req": [
            {
                "ids": {
                    "blob_id": attachment_id,
                    "comment_id": comment_id
                }
            }
        ]}

def report_test_execution(test_run_id, project_id, tc_id, status, report):
    tc_added = add_tc_to_tr(test_run_id, tc_id, status)
    attachment_created = create_attachment(report, project_id)
    created_comment = create_comment(project_id, attachment_created['id'], attachment_created['blob_id'], attachment_created['size'])
    linked_comment = link_comment_to_tr(test_run_id, tc_id, created_comment['id'])
    linked_attachment = link_attachment_to_comment(attachment_created['id'], created_comment['id'])
    return {
        'tc_added': tc_added,
        'attachment_created': attachment_created,
        'created_comment': created_comment,
        'linked_comment': linked_comment,
        'linked_attachment' : linked_attachment
    }