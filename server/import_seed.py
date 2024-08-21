from app import app, db
from models import Country, HsCode, Product, ImportTable, TaxTable
from datetime import datetime
import pandas as pd
import os
import re

# Path to your XLS file (adjust the path if necessary)
xls_file_path = os.path.expanduser('~/Downloads/ICMSData.xlsx')

def normalize_hs_code(code):
    # Remove all non-numeric characters and format as 'xxxxxxxx' from 'xxxx.xx.xx'
    normalized = re.sub(r'\D', '', str(code))
    return normalized

def parse_reg_date(date_str):
    # Check if date_str is a pandas Timestamp
    if isinstance(date_str, pd.Timestamp):
        # Convert Timestamp to datetime object and format it
        return date_str.strftime('%m/%d/%Y')
    elif isinstance(date_str, str):
        # Parse the string into a datetime object and format it
        dt = datetime.strptime(date_str, '%m/%d/%Y %H:%M:%S')
        return dt.strftime('%m/%d/%Y')
    else:
        # Handle unexpected types
        raise TypeError("Expected a string or pandas Timestamp")

# Initialize the application context
with app.app_context():
    # Clear existing tables if needed
    ImportTable.query.delete()
    TaxTable.query.delete()

    # Fetch existing HS Codes and Countries
    hs_codes = HsCode.query.all()
    hs_code_mapping = {normalize_hs_code(hs_code.code): hs_code.id for hs_code in hs_codes}

    countries = Country.query.all()
    country_mapping = {country.code: country.id for country in countries}

    # Read the XLS file for import data
    df = pd.read_excel(xls_file_path)

    # Ensure the DataFrame has the necessary columns
    required_columns = ['YEAR', 'MONTH', 'ENTRY_NUMBER', 'ENTRYSTATUS', 'REG_DATE', 'QUANTITY', 'PLACE_OF_DISCHARGE', 'ORIGIN_COUNTRY_CODE', 'COUNTRY_OF_DESTINATION', 'HSCODE', 'GOOD_DESCRIPTION', 'IMPORT_VAT', 'IMPORT_DUTY', 'EXCISE', 'EXPORT_DUTY', 'IDF', 'RDL']
    if not all(column in df.columns for column in required_columns):
        raise ValueError(f"XLS file must contain the following columns: {', '.join(required_columns)}")

    # Normalize HS Code column in DataFrame
    df['Normalized_HS_CODE'] = df['HSCODE'].apply(normalize_hs_code)

    # Insert Products
    product_mapping = {}
    for index, row in df.iterrows():
        product_name = row['GOOD_DESCRIPTION']
        normalized_hs_code_str = row['Normalized_HS_CODE']

        # Lookup HS code ID in the database
        hs_code_id = hs_code_mapping.get(normalized_hs_code_str)

        if hs_code_id:
            # Check if product already exists
            existing_product = Product.query.filter_by(name=product_name, hs_code_id=hs_code_id).first()
            if not existing_product:
                # Create a new product instance and add to the session
                product = Product(name=product_name, hs_code_id=hs_code_id)
                db.session.add(product)
                db.session.commit()
                print(f"Product {product_name} added with HS Code ID {hs_code_id}")
            else:
                product = existing_product

            # Map the product ID for later use
            product_mapping[(product_name, hs_code_id)] = product.id
            print(product_mapping)
        else:
            print(f"HS Code {row['HSCODE']} not found! Skipping product {product_name}")

    print("Products have been populated successfully.")

    # Insert Imports and Taxes
    for index, row in df.iterrows():
        reg_date = parse_reg_date(row['REG_DATE'])
        entry_number = row['ENTRY_NUMBER']
        entry_status = row['ENTRYSTATUS']
        quantity = row['QUANTITY']
        discharge_port = row['PLACE_OF_DISCHARGE']
        origin_code = row['ORIGIN_COUNTRY_CODE']
        destination_code = row['COUNTRY_OF_DESTINATION']
        normalized_hs_code_str = row['Normalized_HS_CODE']
        product_name = row['GOOD_DESCRIPTION']

        # Tax data
        import_duty = row['IMPORT_DUTY']
        excise_duty = row['EXCISE']
        export_duty = row['EXPORT_DUTY']
        import_vat = row['IMPORT_VAT']
        import_declaration_fee = row['IDF']
        railway_dev_levy = row['RDL'] 

        # Lookup IDs
        origin_id = country_mapping.get(origin_code)
        destination_id = country_mapping.get(destination_code)
        hs_code_id = hs_code_mapping.get(normalized_hs_code_str)
        product_id = product_mapping.get((product_name, hs_code_id))

        if origin_id and destination_id and hs_code_id and product_id:
            # Create a new tax entry
            tax_entry = TaxTable(
                import_duty=import_duty,
                excise_duty=excise_duty,
                export_duty=export_duty,
                import_vat=import_vat,
                import_declaration_fee=import_declaration_fee,
                railway_development_levy=railway_dev_levy
            )
            db.session.add(tax_entry)
            db.session.commit()

            # Create a new import instance and add to the session
            import_entry = ImportTable(
                reg_date=reg_date,
                entry_number=entry_number,
                entry_status=entry_status,
                quantity=quantity,
                discharge_port=discharge_port,
                origin_id=origin_id,
                destination_id=destination_id,
                hscode_id=hs_code_id,
                product_id=product_id
            )
            db.session.add(import_entry)
            db.session.commit()
            print(f"Import record added for origin {origin_code} with HS Code ID {hs_code_id} and Product ID {product_id}")
        else:
            if not origin_id:
                print(f"Origin country code {origin_code} not found! Skipping import record.")
            if not destination_id:
                print(f"Destination country code {destination_code} not found! Skipping import record.")
            if not hs_code_id:
                print(f"HS Code {row['HSCODE']} not found! Skipping import record.")
            if not product_id:
                print(f"Product {product_name} with HS Code ID {hs_code_id} not found! Skipping import record.")

    print("Imports and Taxes have been populated successfully.")
