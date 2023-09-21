import os, requests, json
from dotenv import load_dotenv
import base64

load_dotenv()

github_token = os.environ.get("GITHUB_ACCESS_TOKEN")

def get_conf(app):
    file_request= requests.get(
    url= f'https://api.github.com/repos/remidqa/qa-configurations/contents/{app}.json',
    headers= {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {github_token}'
    }
    )
    data= file_request.json()
    confBytes= base64.b64decode(data['content'])
    confStr= confBytes.decode('ascii')
    conf= json.loads(confStr)
    return conf

def get_postman_conf(app, env):
    conf = get_conf(app)
    return { 
        'postman_collection_id': conf['postman']['postman_collection_id'],
        'postman_environment_id': conf['postman']['postman_environments'][env],
        'testinyio_testcase_id': conf['postman']['testinyio_testcase_id'],
        'testinyio_project_id': conf['testinyio_project_id']
    }