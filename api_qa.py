from flask import Flask
from flask_restx import Resource, Api
#from routes.cypress.run import api as ns_cy_run
from routes.cypress import api as ns_cy
#from routes.cypress.report import api as ns_cy_report
from routes.newman import api as ns_newman
#from routes.newman.run import api as ns_newman_run
#from routes.newman.report import api as ns_newman_report
from routes.reports import api as ns_reports

app = Flask(__name__)
api = Api(app)

api.add_namespace(ns_cy, path='/cypress')
#api.add_namespace(ns_cy_report, path='/cypress/report')
api.add_namespace(ns_newman, path='/newman')
#api.add_namespace(ns_newman_report, path='/newman/report')
api.add_namespace(ns_reports, path='/reports')

if __name__ == '__main__':
    app.run(debug=True)