from flask import Flask, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Food

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
            'project': 'Flask RESTful API',
            'authors': 'John Kimani M. & Priscilla M. Wakahia'
        }, 200)
        return resp
    
    def post(self):
        pass

    def patch(self):
        pass

    def delete(self,id):
        food = Food.query.get(id)
        food.query.delete()
        return f"Deletion Successful"



# EndPoints
api.add_resource(Index, '/', endpoint='home')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
