from flask_restx import Namespace, Resource
from flask import request
from bson.objectid import ObjectId
from functions.send_webhooks import send_webhook
import functions.mongodb as mongodb
import functions.utils as utils

api = Namespace('reports', description='Reports related operations')

@api.route("/runner/<runner>")
class postNewmanReport(Resource):
    def post(self, runner):
        inserted_document = mongodb.insert_document(runner, request.json)
        report_id = str(inserted_document.inserted_id)
        report_status = utils.get_report_status(runner, request.json)
        if report_status == False: return utils.send_json({"msg": "unable to calculate the status of the report"})
        webhook_status = send_webhook(runner, report_id, report_status)
        return utils.send_json({"msg": f"execution succefully saved in db. id: {report_id}"})
    
    def get(self, runner):
        body = request.get_json(force=True, silent=True)
        query = utils.check_query(body)
        documents = mongodb.find_documents(runner, query)
        return utils.send_json(documents)
    
    def delete(self, runner):
        body = request.get_json(force=True, silent=True)
        query = utils.check_query(body)
        deleted_docs = mongodb.delete_decuments(runner, query)
        return utils.send_json({"msg": deleted_docs})

@api.route("/runner/<runner>/report_id/<report_id>")
class getNewmanReport(Resource):
    def get(self, runner, report_id):
        report = mongodb.find_one_document(runner, {"_id": ObjectId(report_id)})
        return utils.send_json(report)