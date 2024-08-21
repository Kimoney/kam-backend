from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Country(db.Model):
    __tablename__ = 'countries'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    code = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return f'<Country: Id: {self.id}, Name: {self.name} Code: {self.code}>'

class HsCode(db.Model):
    __tablename__ = 'hscodes'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<HsCode: Id: {self.id}, Code: {self.code} Description: {self.description}>'

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    hs_code_id = db.Column(db.Integer, ForeignKey('hscodes.id'))

    hs_code = relationship('HsCode', backref=db.backref('products', lazy=True))

    def __repr__(self):
        return f'<Product: Id: {self.id}, Name: {self.name} HS Code: {self.hs_code.code}>'

class ExportTable(db.Model):
    __tablename__ = 'exporttables'
    
    id = db.Column(db.Integer, primary_key=True)
    fob_value = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    unit = db.Column(db.String)
    export_date = db.Column(db.DateTime, default=datetime.utcnow)
    destination_id = db.Column(db.Integer, ForeignKey('countries.id'))
    hscode_id = db.Column(db.Integer, ForeignKey('hscodes.id'))
    product_id = db.Column(db.Integer, ForeignKey('products.id'))

    destination = relationship('Country', backref=db.backref('exports', lazy=True))
    hscode = relationship('HsCode', backref=db.backref('exports', lazy=True))
    product = relationship('Product', backref=db.backref('products', lazy=True))

    def __repr__(self):
        return f'<ExportTable: Id: {self.id}, FOB Value: {self.fob_value} Quantity: {self.quantity} Unit: {self.unit} Export Date: {self.export_date} Destination: {self.destination.name} HS Code: {self.hscode.code}>'

class ImportTable(db.Model):
    __tablename__ = 'importtables'
    
    id = db.Column(db.Integer, primary_key=True)
    reg_date = db.Column(db.DateTime, default=datetime.utcnow)
    entry_number = db.Column(db.Integer)
    entry_status = db.Column(db.String)
    quantity = db.Column(db.Integer)
    discharge_port = db.Column(db.String)
    origin_id = db.Column(db.Integer, ForeignKey('countries.id'))
    destination_id = db.Column(db.Integer, ForeignKey('countries.id'))
    product_id = db.Column(db.Integer, ForeignKey('products.id'))
    hscode_id = db.Column(db.Integer, ForeignKey('hscodes.id'))

    origin = relationship('Country', foreign_keys=[origin_id], backref=db.backref('imports_origin', lazy=True))
    destination = relationship('Country', foreign_keys=[destination_id], backref=db.backref('imports_destination', lazy=True))
    product = relationship('Product', backref=db.backref('imports', lazy=True))
    hscode = relationship('HsCode', backref=db.backref('imports', lazy=True))

    def __repr__(self):
        return f'<ImportTable: Id: {self.id}, Reg Date: {self.reg_date} Entry Number: {self.entry_number} Entry Status: {self.entry_status} Quantity: {self.quantity} Discharge Port: {self.discharge_port} Origin: {self.origin.name} Destination: {self.destination.name} Product: {self.product.name} HS Code: {self.hscode.code}>'

class TaxTable(db.Model):
    __tablename__ = 'taxtables'
    
    id = db.Column(db.Integer, primary_key=True)
    import_duty = db.Column(db.Integer)
    excise_duty = db.Column(db.Integer)
    export_duty = db.Column(db.Integer)
    export_rate = db.Column(db.Integer)
    import_declaration_fee = db.Column(db.Integer)
    railway_development_levy = db.Column(db.Integer)

    def __repr__(self):
        return f'<TaxTable: Id: {self.id}, Import Duty: {self.import_duty} Excise Duty: {self.excise_duty} Export Duty: {self.export_duty} Export Rate: {self.export_rate} Import Declaration Fee: {self.import_declaration_fee} Railway Development Levy: {self.railway_development_levy}>'
