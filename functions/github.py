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
    if 'postman' in conf:
        return { 
            'testinyio_project_id': conf['testinyio_project_id'],
            'postman_collection_id': conf['postman']['postman_collection_id'],
            'postman_environment_id': conf['postman']['postman_environments'][env],
            'folders': conf['postman']['scenarios']
        }
    else:
        return None

def get_cy_conf(app):
    conf = get_conf(app)
    if 'cypress' in conf:
        return { 
            'testinyio_project_id': conf['testinyio_project_id'],
            'scenarios': conf['cypress']['scenarios']
        }
    else:
        return None

def get_full_conf(app, env):
    cy_conf = get_cy_conf(app)
    postman_conf =  get_postman_conf(app, env)
    return {
        "cy": cy_conf,
        "newman": postman_conf
    }