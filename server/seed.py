from app import app
from models import db, Country
import pycountry

with app.app_context():
    # Clear the existing countries table if needed
    Country.query.delete()

    # Fetch and insert country data
    for country in pycountry.countries:
        country_entry = Country(name=country.name, code=country.alpha_2)
        db.session.add(country_entry)
    
    # Commit the changes to the database
    db.session.commit()

    print("Countries have been populated successfully.")
