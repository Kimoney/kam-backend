from flask import Flask, jsonify, request, abort
from models import db, Country, HsCode, Product, ExportTable, ImportTable, TaxTable

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your-database.db'
app.config['SECRET_KEY'] = 'your_secret_key' 
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not 'username' in data or not 'password' in data:
        abort(400)

    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({'message': 'Logged in successfully'}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/countries', methods=['GET'])
@login_required
def get_countries():
    countries = Country.query.all()
    return jsonify([{
        'id': country.id,
        'name': country.name,
        'code': country.code
    } for country in countries])

# Similarly, protect other routes as needed


@app.route('/countries', methods=['GET'])
def get_countries():
    countries = Country.query.all()
    return jsonify([{
        'id': country.id,
        'name': country.name,
        'code': country.code
    } for country in countries])

@app.route('/countries/<int:id>', methods=['GET'])
def get_country(id):
    country = Country.query.get_or_404(id)
    return jsonify({
        'id': country.id,
        'name': country.name,
        'code': country.code
    })

@app.route('/countries', methods=['POST'])
def create_country():
    data = request.get_json()
    if not data or not 'name' in data or not 'code' in data:
        abort(400)

    country = Country(name=data['name'], code=data['code'])
    db.session.add(country)
    db.session.commit()
    return jsonify({'id': country.id, 'name': country.name, 'code': country.code}), 201

@app.route('/countries/<int:id>', methods=['PUT'])
def update_country(id):
    country = Country.query.get_or_404(id)
    data = request.get_json()

    if 'name' in data:
        country.name = data['name']
    if 'code' in data:
        country.code = data['code']

    db.session.commit()
    return jsonify({'id': country.id, 'name': country.name, 'code': country.code})

@app.route('/countries/<int:id>', methods=['DELETE'])
def delete_country(id):
    country = Country.query.get_or_404(id)
    db.session.delete(country)
    db.session.commit()
    return jsonify({'result': True})

# Similarly, you can create routes for HsCode, Product, ExportTable, ImportTable, and TaxTable.

@app.route('/hscodes', methods=['GET'])
def get_hscodes():
    hscodes = HsCode.query.all()
    return jsonify([{
        'id': hscode.id,
        'code': hscode.code,
        'description': hscode.description
    } for hscode in hscodes])

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': product.id,
        'name': product.name,
        'hs_code_id': product.hs_code_id
    } for product in products])

@app.route('/exporttables', methods=['GET'])
def get_exporttables():
    exports = ExportTable.query.all()
    return jsonify([{
        'id': export.id,
        'fob_value': export.fob_value,
        'quantity': export.quantity,
        'unit': export.unit,
        'export_date': export.export_date,
        'destination_id': export.destination_id,
        'hscode_id': export.hscode_id
    } for export in exports])

@app.route('/importtables', methods=['GET'])
def get_importtables():
    imports = ImportTable.query.all()
    return jsonify([{
        'id': imp.id,
        'reg_date': imp.reg_date,
        'entry_number': imp.entry_number,
        'entry_status': imp.entry_status,
        'quantity': imp.quantity,
        'discharge_port': imp.discharge_port,
        'origin_id': imp.origin_id,
        'destination_id': imp.destination_id,
        'product_id': imp.product_id,
        'hscode_id': imp.hscode_id
    } for imp in imports])

@app.route('/taxtables', methods=['GET'])
def get_taxtables():
    taxes = TaxTable.query.all()
    return jsonify([{
        'id': tax.id,
        'import_duty': tax.import_duty,
        'excise_duty': tax.excise_duty,
        'export_duty': tax.export_duty,
        'export_rate': tax.export_rate,
        'import_declaration_fee': tax.import_declaration_fee,
        'railway_development_levy': tax.railway_development_levy
    } for tax in taxes])

if __name__ == '__main__':
    app.run(debug=True)
