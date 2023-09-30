from flask_restx import Namespace, Resource
from flask import request
from bson.objectid import ObjectId
import functions.mongodb as mongodb
import functions.utils as utils

api = Namespace('reports', description='Reports related operations')

@api.route("/report_id/<report_id>")
class get_report_by_id(Resource):
    def get(self, report_id):
        query = utils.check_query({"query": {"_id": report_id}})
        documents = mongodb.find_documents('executions', query)
        return utils.send_json(documents)

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
