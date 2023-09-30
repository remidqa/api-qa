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
    if file_request.status_code != 200:
        return {"status": file_request.status_code, "data": file_request.json()}
    data= file_request.json()
    confBytes= base64.b64decode(data['content'])
    confStr= confBytes.decode('ascii')
    conf= json.loads(confStr)
    return {"status": file_request.status_code, "data": conf}

def get_postman_conf(app, env):
    conf = get_conf(app)
    if conf['status'] != 200:
        return {'err': f"no file found at '/{app}.json'"}
    if conf.get('data', {}).get('postman', {}):
        data = conf['data']
        postman_conf = {
            'testinyio_project_id': data['testinyio_project_id'] if data.get('testinyio_project_id', {}) else None,
            'postman_collection_id': data['postman']['postman_collection_id'] if data.get('postman', {}).get('postman_collection_id', {}) else None,
            'postman_environment_id': data['postman']['postman_environments'][env] if data.get('postman', {}).get('postman_environments', {}).get(env, {}) else None,
            'scenarios': data['postman']['scenarios'] if data.get('postman', {}).get('scenarios', {}) else None
        }
        if any(value is None for value in postman_conf.values()):
            return {'err': f"wrong or missing values for '{', '.join({key: value for key, value in postman_conf.items() if value is None}.keys())}'"}
        else:
            return postman_conf
    else:
        return {'err': 'no postman configuration found in .json file'}

def get_cy_conf(app, env):
    conf = get_conf(app)
    if conf['status'] != 200:
        return {'err': f"no file found at '/{app}.json'"}
    if conf.get('data', {}).get('cypress', {}):
        data = conf['data']
        cy_conf = {
            'testinyio_project_id': data['testinyio_project_id'] if data.get('testinyio_project_id', {}) else None,
            'scenarios': data['cypress']['scenarios'] if data.get('cypress', {}).get('scenarios', {}) else None,
            'env': env if data.get('cypress', {}).get('envs', {}) and env in data['cypress']['envs'] else None
        }
        if any(value is None for value in cy_conf.values()):
            return {'err': f"wrong or missing values for '{', '.join({key: value for key, value in cy_conf.items() if value is None}.keys())}'"}
        else:
            return cy_conf
        
    else:
        return {'err': 'no cypress configuration found in .json file'}

def get_full_conf(app, env):
    cy_conf = get_cy_conf(app, env)
    postman_conf =  get_postman_conf(app, env)
    return {
        'testinyio_project_id': cy_conf["testinyio_project_id"] if cy_conf.get('testinyio_project_id') else postman_conf["testinyio_project_id"] if postman_conf.get('testinyio_project_id') else None,
        "cy": cy_conf,
        "newman": postman_conf
    }