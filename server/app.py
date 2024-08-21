from flask import Flask, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Country, HsCode, Product
from resources import ExportResource, ImportResource, LoginResource, LogoutResource, CountriesResource, CountryResource, HsCodesResource, ProductsResource, ExportTablesResource,  ImportTablesResource, TaxTablesResource

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

@app.route('/')
def index():
    return '<h1>Welcome To Flask</h1>'

# Class-Based Views
class Index(Resource):
    def get(self):
        resp = make_response({
            'project': 'KAM Hackathon',
            'authors': 'Joy, Kimani, Brian'
        }, 200)
        return resp

# EndPoints
api.add_resource(Index, '/', endpoint='home')
api.add_resource(ExportResource, '/exports', '/exports/<int:export_id>')  # Add this line
api.add_resource(ImportResource, '/import')

api.add_resource(LoginResource, '/login')
api.add_resource(LogoutResource, '/logout')
api.add_resource(CountriesResource, '/countries')
api.add_resource(CountryResource, '/countries/<int:id>')
api.add_resource(HsCodesResource, '/hscodes')
api.add_resource(ProductsResource, '/products')
api.add_resource(ExportTablesResource, '/exporttables')
api.add_resource(ImportTablesResource, '/importtables')
api.add_resource(TaxTablesResource, '/taxtables')



if __name__ == '__main__':
    app.run(port=5555, debug=True)
