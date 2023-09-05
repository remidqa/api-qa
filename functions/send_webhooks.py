import json
import requests, os
from dotenv import load_dotenv

load_dotenv()

slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
api_qa_ext_url = os.environ.get("API_QA_EXT_URL")

template = {
    "text": "overflow",
    "blocks": [
        {
            "type": "section",
            "block_id": "section 890",
            "text": {
                "type": "mrkdwn",
                "text": ""
            }
        }
    ],
    "attachments": [
        {
            "color": "",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ""
                    }
                }
            ]
        }
    ]
}

def send_webhook(runner, report_id, status):
    
    tp = template

    if runner == "cypress": # Customize cypress webhook
          tp["blocks"][0]["text"]["text"] = "CYPRESS EXECUTION RUN"
          
          if status == "success": # Customize webhook if all executions OK
              tp["attachments"][0]["color"] = "1fad00"
              tp["attachments"][0]["blocks"][0]["text"]["text"] = f":white_check_mark: All assertions OK : <{api_qa_ext_url}/reports/runner/cypress/report_id/{report_id}|See full .json report>"
          elif status == "failure": # Customize webhook if a failed execution
              tp["attachments"][0]["color"] = "a80000"
              tp["attachments"][0]["blocks"][0]["text"]["text"] = f":x: Something went wrong : <{api_qa_ext_url}/reports/runner/cypress/report_id/{report_id}|See full .json report>"
  

    elif runner == "newman": # Customize newman webhook
          tp["blocks"][0]["text"]["text"] = "NEWMAN EXECUTION RUN"

          if status == "success": # Customize webhook if all executions OK
              tp["attachments"][0]["color"] = "1fad00"
              tp["attachments"][0]["blocks"][0]["text"]["text"] = f":white_check_mark: All assertions OK : <{api_qa_ext_url}/reports/runner/newman/report_id/{report_id}|See full .json report>"
          elif status == "failure": # Customize webhook if a failed execution
              tp["attachments"][0]["color"] = "a80000"
              tp["attachments"][0]["blocks"][0]["text"]["text"] = f":x: Something went wrong : <{api_qa_ext_url}/reports/runner/newman/report_id/{report_id}|See full .json report>"

    payload = json.dumps(tp)
    
    headers = {
      'Content-type': 'application/json'
    }

    r = requests.post(url=slack_webhook_url, data=payload, headers=headers)
    return r.text
