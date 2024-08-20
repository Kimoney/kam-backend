from app import app, db
from models import Country, HsCode, Product, ExportTable, ImportTable, TaxTable
from datetime import datetime
import pycountry

# Define some mock data for HS Codes, Countries, Products, etc.
hs_codes_data = [
    {"code": "4804.11.00", "description": "Unbleached kraft liner"},
    {"code": "4804.21.00", "description": "Unbleached sack kraft"},
    {"code": "4804.31.00", "description": "Unbleached kraft paper"},
    {"code": "4805.11.00", "description": "Sem-chemical fluting"},
    {"code": "4804.39.00", "description": "Other bleached kraft Paper and paperboard weighing 150 g/m2 or less"},
    {"code": "4804.42.00", "description": "Bleached krast liner of more than 150 gms"},
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
    {"code": "7217.20.00", "description": "Gi wire"},
    {"code": "2523.29.00", "description": "Portland cement"},
]

products_data = [
    {"name": "Product 1", "hs_code_id": 1},
    {"name": "Product 2", "hs_code_id": 2}
]

# Initialize the application context
with app.app_context():
    # Create tables
    db.create_all()

    # Insert HS Codes
    for hs in hs_codes_data:
        new_hs_code = HsCode(code=hs["code"], description=hs["description"])
        db.session.add(new_hs_code)
    
    # Commit HS Codes to the database
    db.session.commit()

    # Retrieve HS Codes to link with products
    hs_codes = HsCode.query.all()
    hs_code_mapping = {hs_code.code: hs_code for hs_code in hs_codes}

    print("Database seeded successfully!")

    # Clear the existing countries table if needed
    Country.query.delete()

    # Fetch and insert country data
    for country in pycountry.countries:
        country_entry = Country(name=country.name, code=country.alpha_2)
        db.session.add(country_entry)
    
    # Commit the changes to the database
    db.session.commit()

    print("Countries have been populated successfully.")
