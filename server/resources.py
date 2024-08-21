from flask import Flask, jsonify, request, abort
from flask_restful import Resource
from flask_login import LoginManager, login_user, logout_user, login_required
from models import db, Country, HsCode, Product, ExportTable, ImportTable, TaxTable, User

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'loginresource'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        if not data or not 'username' in data or not 'password' in data:
            abort(400)

        user = User.query.filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            login_user(user)
            return {'message': 'Logged in successfully'}, 200
        else:
            return {'message': 'Invalid username or password'}, 401


class LogoutResource(Resource):
    @login_required
    def post(self):
        logout_user()
        return {'message': 'Logged out successfully'}, 200


class CountriesResource(Resource):
    @login_required
    def get(self):
        countries = Country.query.all()
        return [{'id': country.id, 'name': country.name, 'code': country.code} for country in countries]

    def post(self):
        data = request.get_json()
        if not data or not 'name' in data or not 'code' in data:
            abort(400)

        country = Country(name=data['name'], code=data['code'])
        db.session.add(country)
        db.session.commit()
        return {'id': country.id, 'name': country.name, 'code': country.code}, 201


class CountryResource(Resource):
    def get(self, id):
        country = Country.query.get_or_404(id)
        return {'id': country.id, 'name': country.name, 'code': country.code}

    def put(self, id):
        country = Country.query.get_or_404(id)
        data = request.get_json()

        if 'name' in data:
            country.name = data['name']
        if 'code' in data:
            country.code = data['code']

        db.session.commit()
        return {'id': country.id, 'name': country.name, 'code': country.code}

    def delete(self, id):
        country = Country.query.get_or_404(id)
        db.session.delete(country)
        db.session.commit()
        return {'result': True}


class HsCodesResource(Resource):
    def get(self):
        hscodes = HsCode.query.all()
        return [{'id': hscode.id, 'code': hscode.code, 'description': hscode.description} for hscode in hscodes]


class ProductsResource(Resource):
    def get(self):
        products = Product.query.all()
        return [{'id': product.id, 'name': product.name, 'hs_code_id': product.hs_code_id} for product in products]


class ExportTablesResource(Resource):
    def get(self):
        exports = ExportTable.query.all()
        return [{
            'id': export.id,
            'fob_value': export.fob_value,
            'quantity': export.quantity,
            'unit': export.unit,
            'export_date': export.export_date,
            'destination_id': export.destination_id,
            'hscode_id': export.hscode_id
        } for export in exports]


class ImportTablesResource(Resource):
    def get(self):
        imports = ImportTable.query.all()
        return [{
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
        } for imp in imports]


class TaxTablesResource(Resource):
    def get(self):
        taxes = TaxTable.query.all()
        return [{
            'id': tax.id,
            'import_duty': tax.import_duty,
            'excise_duty': tax.excise_duty,
            'export_duty': tax.export_duty,
            'export_rate': tax.export_rate,
            'import_declaration_fee': tax.import_declaration_fee,
            'railway_development_levy': tax.railway_development_levy
        } for tax in taxes]

class ExportResource(Resource):
    def get(self):
        exports = ExportTable.query.all()
        result = []

        for export in exports:
            export_data = {
                "id": export.id,
                "Year": export.export_date.year,
                "Month": export.export_date.month,
                "DESTINATION": export.destination.code,
                "COUNTRYNAME": export.destination.name,
                "HS CODE": export.hscode.code,
                "SHORT_DESC": export.hscode.description,
                "QUANTITY": export.quantity,
                "UNIT": export.unit,
                "FOB_VALUE": export.fob_value
            }
            result.append(export_data)
        
        return jsonify(result)

class ImportResource(Resource):
    def get(self):
        imports = ImportTable.query.all()
        result = []

        # Fetch the tax information
        tax_info = TaxTable.query.first()  # Assuming there's only one row, adjust if necessary

        for imp in imports:
            import_data = {
                'id': imp.id,
                'reg_date': imp.reg_date,
                'entry_number': imp.entry_number,
                'entry_status': imp.entry_status,
                'quantity': imp.quantity,
                'discharge_port': imp.discharge_port,
                'origin_id': imp.origin.id,
                'origin_name': imp.origin.name,
                'origin_code': imp.origin.code,
                'destination_id': imp.destination.id,
                'destination_name': imp.destination.name,
                'destination_code': imp.destination.code,
                'product_id': imp.product.id if imp.product else None,
                'product_name': imp.product.name if imp.product else None,
                'hscode_id': imp.hscode.id if imp.hscode else None,
                'hscode_code': imp.hscode.code if imp.hscode else None,
                'hscode_description': imp.hscode.description if imp.hscode else None,
                'import_duty': tax_info.import_duty if tax_info else None,
                'excise_duty': tax_info.excise_duty if tax_info else None,
                'export_duty': tax_info.export_duty if tax_info else None,
                'import_vat': tax_info.import_vat if tax_info else None,
                'import_declaration_fee': tax_info.import_declaration_fee if tax_info else None,
                'railway_development_levy': tax_info.railway_development_levy if tax_info else None
            }
            result.append(import_data)
        
        return jsonify(result)