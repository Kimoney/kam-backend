from app import app, db
from models import Country, HsCode, Product, ExportTable
from datetime import datetime
import pycountry
import pandas as pd
import os
import re

# Path to your XLS file (adjust the path if necessary)
xls_file_path = os.path.expanduser('~/Downloads/kamexports.xls')

def normalize_hs_code(code):
    # Remove all non-numeric characters and format as 'xxxxxxxx' from 'xxxx.xx.xx'
    normalized = re.sub(r'\D', '', str(code))
    return normalized

def parse_export_date(year, month):
    # Combine Year and Month columns to create a datetime object
    return datetime(year=int(year), month=int(month), day=1)

# Initialize the application context
with app.app_context():
    # Create tables
    db.create_all()
    
    # Clear existing tables if needed
    HsCode.query.delete()
    Country.query.delete()
    Product.query.delete()
    ExportTable.query.delete()

    # Insert HS Codes
    hs_codes_data = [
        {"code": "4804.11.00", "description": "Unbleached kraft liner"},
        {"code": "4804.21.00", "description": "Unbleached sack kraft"},
        {"code": "4804.31.00", "description": "Unbleached kraft paper"},
        {"code": "4805.11.00", "description": "Sem-chemical fluting"},
        {"code": "4804.39.00", "description": "Other bleached kraft Paper and paperboard weighing 150 g/m2 or less"},
        {"code": "4804.42.00", "description": "Bleached kraft liner of more than 150 gms"},
        {"code": "2523.10.00", "description": "Cement Clinker"},
        {"code": "7207.11.00", "description": "Billets"},
        {"code": "7213.91.10", "description": "Wire rods"},
        {"code": "4819.30.00", "description": "Paper and bags"},
        {"code": "4819.40.00", "description": "Paper and bags"},
        {"code": "4819.10.00", "description": "Cartons"},
        {"code": "4811.59.90", "description": "PE Comet Paper"},
        {"code": "7213.10.00", "description": "TMT/construction steel"},
        {"code": "7216.21.00", "description": "Angles"},
        {"code": "7216.61.00", "description": "Flats"},
        {"code": "7216.16.00", "description": "Channels"},
        {"code": "7217.20.00", "description": "GI wire"},
        {"code": "2523.29.00", "description": "Portland cement"},
    ]

    # Insert HS Codes into the database
    for hs in hs_codes_data:
        new_hs_code = HsCode(code=hs["code"], description=hs["description"])
        db.session.add(new_hs_code)

    # Commit HS Codes to the database
    db.session.commit()

    # Fetch and insert country data
    for country in pycountry.countries:
        country_entry = Country(name=country.name, code=country.alpha_2)
        db.session.add(country_entry)

    # Commit the country data to the database
    db.session.commit()

    print("Countries have been populated successfully.")

    # Retrieve HS Codes to link with products
    hs_codes = HsCode.query.all()
    hs_code_mapping = {normalize_hs_code(hs_code.code): hs_code.id for hs_code in hs_codes}
    print(hs_code_mapping)

    # Read the XLS file for product data
    df = pd.read_excel(xls_file_path)

    # Ensure the DataFrame has the necessary columns
    required_columns = ['SHORT_DESC', 'HS CODE', 'Year', 'Month', 'DESTINATION', 'QUANTITY', 'UNIT', 'FOB_VALUE']
    if not all(column in df.columns for column in required_columns):
        raise ValueError(f"XLS file must contain the following columns: {', '.join(required_columns)}")

    # Normalize HS Code column in DataFrame
    df['Normalized_HS_CODE'] = df['HS CODE'].apply(normalize_hs_code)

    # Insert Products
    product_mapping = {}
    for index, row in df.iterrows():
        product_name = row['SHORT_DESC']
        normalized_hs_code_str = row['Normalized_HS_CODE']

        # Lookup HS code ID in the database
        hs_code_id = hs_code_mapping.get(normalized_hs_code_str)
        print(hs_code_id)

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
        else:
            print(f"HS Code {row['HS CODE']} not found! Skipping product {product_name}")

    print("Products have been populated successfully.")

    # Fetch country data for lookup
    country_mapping = {country.code: country.id for country in Country.query.all()}

    # Insert Exports
    for index, row in df.iterrows():
        year = row['Year']
        month = row['Month']
        destination_code = row['DESTINATION']
        normalized_hs_code_str = row['Normalized_HS_CODE']
        quantity = row['QUANTITY']
        unit = row['UNIT']
        fob_value = row['FOB_VALUE']
        product_name = row['SHORT_DESC']

        # Create export date from Year and Month
        export_date = parse_export_date(year, month)

        # Lookup HS code ID in the database
        hs_code_id = hs_code_mapping.get(normalized_hs_code_str)

        # Lookup destination country ID
        destination_id = country_mapping.get(destination_code)

        # Lookup product ID
        product_id = product_mapping.get((product_name, hs_code_id))

        if hs_code_id and destination_id and product_id:
            # Create a new export instance and add to the session
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
            print(f"Export record added for destination {destination_code} with HS Code ID {hs_code_id} and Product ID {product_id}")
        else:
            if not hs_code_id:
                print(f"HS Code {row['HS CODE']} not found! Skipping export record.")
            if not destination_id:
                print(f"Destination country code {destination_code} not found! Skipping export record.")
            if not product_id:
                print(f"Product {product_name} with HS Code ID {hs_code_id} not found! Skipping export record.")

    print("Exports have been populated successfully.")
