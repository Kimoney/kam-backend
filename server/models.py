from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Country(db.Model):
    __tablename__ = 'countries'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    code = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Country: Id: {self.id}, Name: {self.name} Ingredients: {self.code}>'

class HsCode(db.Model):
    __tablename__ = 'hscodes'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    
    def __repr__(self):
        return f'<HsCode: Id: {self.id}, Code: {self.code} Description: {self.description}>'
    
class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    hs_code_id = db.Column(db.Integer, db.ForeignKey('hscodes.id'))
    
    hs_code = db.relationship('HsCode', backref=db.backref('products', lazy=True))
    
    def __repr__(self):
        return f'<Product: Id: {self.id}, Name: {self.name} HS Code: {self.hs_code.code}>'