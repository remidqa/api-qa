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
        report = request.json
        inserted_report = mongodb.insert_document("newman", report)
        inserted_id = str(inserted_report.inserted_id)
        return utils.send_json({"status": 200, "msg": f"succesfully inserted {runner} report", "data": {"runner": runner, "inserted_id": inserted_id}})
    
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

#@api.route("/runner/<runner>/report_id/<report_id>")
#class getNewmanReport(Resource):
#    def get(self, runner, report_id):
#        report = mongodb.find_one_document(runner, {"_id": ObjectId(report_id)})
#        return utils.send_json(report)