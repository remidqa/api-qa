from flask import Flask
from flask_restx import Api
from routes.cypress import api as ns_cy
from routes.newman import api as ns_newman
from routes.reports import api as ns_reports

app = Flask(__name__)
api = Api(app)

api.add_namespace(ns_cy, path='/cypress')
api.add_namespace(ns_newman, path='/newman')
api.add_namespace(ns_reports, path='/reports')

if __name__ == '__main__':
    app.run(debug=True)