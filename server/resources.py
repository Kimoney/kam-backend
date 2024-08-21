from flask_restful import Resource
from models import db, ExportTable
from flask import jsonify

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
