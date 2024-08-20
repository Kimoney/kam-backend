from models import db, Food
from app import app

with app.app_context():

    Food.query.delete()

    food1 = Food(name='Fries', ingredients='Waru, Cooking Oil, Salt')
    food2 = Food(name='Cassava', ingredients='Cassava, Salt')
    food3 = Food(name='Beef', ingredients='Meat, Salt')
    
    db.session.add(food1)
    db.session.commit()
    db.session.add(food2)
    db.session.commit()
    db.session.add(food3)
    db.session.commit()
