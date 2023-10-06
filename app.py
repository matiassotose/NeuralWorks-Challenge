from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import csv
from models.trip import Trip
from datetime import datetime


app = Flask(__name__)

db_uri = 'postgresql://postgres:12345@localhost:5432/neuralworks'

engine = create_engine(db_uri)
Session = sessionmaker(bind=engine)

@app.route('/trips', methods=['POST'])
def ingest_csv():
    try:
        session = Session()
        
        file = request.files['file']
        
        if not file:
            return jsonify({'message': 'No file uploaded'}), 400
        
        text_data = file.read().decode('utf-8')
        csv_data = csv.DictReader(text_data.splitlines())
        
        for row in csv_data:
            trip = Trip(
                region=row['region'],
                origin_coord=row['origin_coord'],
                destination_coord=row['destination_coord'],
                datetime=datetime.strptime(row['datetime'], '%Y-%m-%d %H:%M:%S'),
                datasource=row['datasource']
            )
            session.add(trip)
        session.commit()
        return jsonify({'message': 'CSV uploaded successfully'}), 200
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
    finally:
        session.close()
        
if __name__ == '__main__':
    app.run(debug=True)