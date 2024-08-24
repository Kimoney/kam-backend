from flask import Flask, jsonify, request, abort
from flask_restful import Resource
from flask_login import LoginManager, login_user, logout_user, login_required
from models import db, Country, HsCode, Product, ExportTable, ImportTable, TaxTable, User
import os
import re
from datetime import datetime
import pandas as pd

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'loginresource'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class RegisterResource(Resource):
    def post(self):
        data = request.get_json()

        # Validate input data
        required_fields = ['username', 'password']
        for field in required_fields:
            if not data.get(field):
                return {'message': f'{field} is required'}, 400

        # Check if the user already exists
        if User.query.filter_by(username=data['username']).first():
            return {'message': 'Username already taken'}, 409

        # Create a new user instance
        try:
            new_user = User(
                username=data['username'],  # Use username from input
                password=data['password']  # Use password from input
            )
            # new_user.set_password(data['password'])  # Hash the password

            # Add and commit the new user to the database
            db.session.add(new_user)
            db.session.commit()

            return {'message': 'Registration successful'}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500


class LoginResource(Resource):
    def post(self):
        data = request.get_json()

        # Validate that required fields are present in the request
        if not data or not data.get('username') or not data.get('password'):
            return {'message': 'Username and password are required'}, 400

        # Attempt to retrieve the user from the database
        user = User.query.filter_by(username=data['username']).first()

        # Validate the user exists and the password is correct
        pwd = data['password']
        if user and user.password:
            # login_user(user)  # Log the user in using Flask-Login
            return {'message': 'Logged in successfully'}, 200
        else:
            return {'message': 'Invalid username or password'}, 401

class LogoutResource(Resource):
    @login_required
    def post(self):
        logout_user()
        return {'message': 'Logged out successfully'}, 200


class CountriesResource(Resource):
    # @login_required
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
                'origin_id': imp.origin.id if imp.origin else None,
                'origin_name': imp.origin.name if imp.origin else None,
                'origin_code': imp.origin.code if imp.origin else None,
                'destination_id': imp.destination.id if imp.destination else None,
                'destination_name': imp.destination.name if imp.destination else None,
                'destination_code': imp.destination.code if imp.destination else None,
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

    
class AnalyzedCountriesResource(Resource):
    def get(self):
        # Query to get unique country IDs from both ExportTable and ImportTable
        export_country_ids = db.session.query(ExportTable.destination_id).distinct().subquery()
        import_country_ids = db.session.query(ImportTable.origin_id).distinct().subquery()
        
        all_country_ids = db.session.query(db.func.coalesce(export_country_ids.c.destination_id, import_country_ids.c.origin_id)).distinct().all()
        
        # Extract country IDs from the query result
        country_ids = [row[0] for row in all_country_ids if row[0] is not None]
        
        # Fetch country details using unique IDs
        countries = Country.query.filter(Country.id.in_(country_ids)).all()
        
        # Prepare response data
        response_data = [{'id': country.id, 'name': country.name, 'code': country.code} for country in countries]
        
        return jsonify(response_data)
    
def normalize_hs_code(code):
    return re.sub(r'\D', '', str(code))

def parse_export_date(year, month):
    return datetime(year=int(year), month=int(month), day=1)

def process_file(filepath):
    hs_codes = HsCode.query.all()
    hs_code_mapping = {normalize_hs_code(hs_code.code): hs_code.id for hs_code in hs_codes}

    country_mapping = {country.code: country.id for country in Country.query.all()}

    df = pd.read_excel(filepath)

    required_columns = ['SHORT_DESC', 'HS CODE', 'Year', 'Month', 'DESTINATION', 'QUANTITY', 'UNIT', 'FOB_VALUE']
    if not all(column in df.columns for column in required_columns):
        raise ValueError(f"XLS file must contain the following columns: {', '.join(required_columns)}")

    df['Normalized_HS_CODE'] = df['HS CODE'].apply(normalize_hs_code)

    product_mapping = {}
    for index, row in df.iterrows():
        product_name = row['SHORT_DESC']
        normalized_hs_code_str = row['Normalized_HS_CODE']
        hs_code_id = hs_code_mapping.get(normalized_hs_code_str)

        if hs_code_id:
            existing_product = Product.query.filter_by(name=product_name, hs_code_id=hs_code_id).first()
            if not existing_product:
                product = Product(name=product_name, hs_code_id=hs_code_id)
                db.session.add(product)
                db.session.commit()
                product_id = product.id
            else:
                product_id = existing_product.id
            product_mapping[(product_name, hs_code_id)] = product_id
        else:
            print(f"HS Code {row['HS CODE']} not found! Skipping product {product_name}")

    for index, row in df.iterrows():
        year = row['Year']
        month = row['Month']
        destination_code = row['DESTINATION']
        normalized_hs_code_str = row['Normalized_HS_CODE']
        quantity = row['QUANTITY']
        unit = row['UNIT']
        fob_value = row['FOB_VALUE']
        product_name = row['SHORT_DESC']

        export_date = parse_export_date(year, month)
        hs_code_id = hs_code_mapping.get(normalized_hs_code_str)
        destination_id = country_mapping.get(destination_code)
        product_id = product_mapping.get((product_name, hs_code_id))

        if hs_code_id and destination_id and product_id:
            export_entry = ExportTable(
                fob_value=fob_value,
                quantity=quantity,
                unit=unit,
                export_date=export_date,
                destination_id=destination_id,
                hscode_id=hs_code_id,
                product_id=product_id
            )
            db.session.add(export_entry)
            db.session.commit()
        else:
            if not hs_code_id:
                print(f"HS Code {row['HS CODE']} not found! Skipping export record.")
            if not destination_id:
                print(f"Destination country code {destination_code} not found! Skipping export record.")
            if not product_id:
                print(f"Product {product_name} with HS Code ID {hs_code_id} not found! Skipping export record.")


class FileUpload(Resource):
    def post(self):
        if 'file' not in request.files:
            return {"error": "No file part"}, 400

        file = request.files['file']
        if file.filename == '':
            return {"error": "No selected file"}, 400

        if file and allowed_file(file.filename):
            filepath = os.path.join('/tmp', file.filename)
            file.save(filepath)

            try:
                process_file(filepath)
                return {"message": "File processed successfully"}, 200
            except Exception as e:
                return {"error": str(e)}, 500

        return {"error": "Invalid file type"}, 400

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['xlsx']
