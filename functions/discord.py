import requests, os
from dotenv import load_dotenv

load_dotenv()

discord_webhook = os.environ.get("DISCORD_WEBHOOK")
api_qa_ext_url = os.environ.get("API_QA_EXT_URL")

def generate_msg(id, status, app, env):
    return  {
    "username": "qa-bot",
    "embeds": [
        {
            "title": "Non-regression execution ended",
            "description": f"**{status.upper()}**: non-regression executions ended for app **'{app}'** in **'{env}'** environment. To get more details :  [see full report]({api_qa_ext_url}/reports/report_id/{id})",
            "color": 13509436 if status == 'failure' else 3591969
        }
    ]}

def send_discord_webhook(id, status, app, env):
    sent_webhook = requests.post(
        url= discord_webhook,
        json= generate_msg(id, status, app, env)
    )
    return sent_webhook