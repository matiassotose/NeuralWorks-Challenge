from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import csv
from models.trip import Trip
from datetime import datetime
import redis
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

if os.getenv('DB_URI'):
    db_uri = os.getenv('DB_URI')
else:
    db_uri = 'postgresql://postgres:password@localhost:5432/neuralworks'

engine = create_engine(db_uri)
Session = sessionmaker(bind=engine)

if os.getenv('REDIS_HOST'):
    redis_host = os.getenv('REDIS_HOST')
else:
    redis_host = 'localhost'
    
if os.getenv('REDIS_PORT'):
    redis_port = os.getenv('REDIS_PORT')
else:
    redis_port = 6379
    
if os.getenv('REDIS_DB'):
    redis_db = os.getenv('REDIS_DB')
else:
    redis_db = 0

r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

# redis ingestion status values:
# 0: no ingestion in progress
# 1: ingestion in progress
# -1: last ingestion failed

# 1. a. Ingerir los viajes bajo demanda
@app.route('/trips', methods=['POST'])
def ingest_csv():
    r.set('ingestion_status', 1)
    try:
        session = Session()
        
        file = request.files['file']
        
        if not file:
            return jsonify({'message': 'No file uploaded'}), 400
        
        text_data = file.read().decode('utf-8')
        csv_data = csv.DictReader(text_data.splitlines())
        
        for row in csv_data:
            # Extract x and y coordinates from origin and destination columns
            origin_coord = tuple(map(float, row['origin_coord'][7:-1].split()))
            destination_coord = tuple(map(float, row['destination_coord'][7:-1].split()))
            
            trip = Trip(
                region=row['region'],
                origin_x=origin_coord[0],
                origin_y=origin_coord[1],
                destination_x=destination_coord[0],
                destination_y=destination_coord[1],
                datetime=datetime.strptime(row['datetime'], '%Y-%m-%d %H:%M:%S'),
                datasource=row['datasource']
            )
            session.add(trip)
        session.commit()
        r.set('ingestion_status', 0)
        return jsonify({'message': 'CSV uploaded successfully'}), 200
    
    except Exception as e:
        r.set('ingestion_status', -1)
        return jsonify({'message': str(e)}), 500
    
    finally:
        session.close()

        
# 2. Un servicio que es capaz de proporcionar la siguiente funcionalidad:
#   a. Devuelve el promedio semanal de la cantidad de viajes para un área definida por un bounding box y la región

@app.route('/trips/average', methods=['GET'])
def get_average_trips():
    try:
        session = Session()
        
        region = request.args.get('region')
        bbox = request.args.get('bbox')
        
        if not region:
            return jsonify({'message': 'Missing region parameter'}), 400
        
        if not bbox:
            return jsonify({'message': 'Missing bbox parameter'}), 400
        
        # bbox should be a string of 4 coordinates separated by commas
        # e.g. bbox=1.0,2.0,3.0,4.0
        # representing the bottom left and top right corners of a rectangle
        bbox = tuple(map(float, bbox.split(',')))
        
        query = session.query(Trip).filter(Trip.region == region)
        query = query.filter(Trip.origin_x >= bbox[0], Trip.origin_x <= bbox[2])
        query = query.filter(Trip.origin_y >= bbox[1], Trip.origin_y <= bbox[3])
        query = query.filter(Trip.destination_x >= bbox[0], Trip.destination_x <= bbox[2])
        query = query.filter(Trip.destination_y >= bbox[1], Trip.destination_y <= bbox[3])
        
        if query.count() == 0:
            return jsonify({'message': 'No trips found for this region and bbox'}), 404
        
        # Get the total number of weeks in the dataset by getting the difference
        # between the maximum and minimum datetime values and dividing by 7
        weeks = (query.order_by(Trip.datetime.desc()).first().datetime - query.order_by(Trip.datetime.asc()).first().datetime).days / 7

        # Get the total number of trips in the dataset
        total_trips = query.count()
        
        # Calculate the average number of trips per week
        average = total_trips / weeks
        
        return jsonify({'average_trips': average}), 200
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500
        
        
# b. Informar sobre el estado de la ingesta de datos sin utilizar una solución de polling
# En este caso se leera una variable de redis que se actualiza cada vez que se ingresa un nuevo archivo

@app.route('/trips/ingestion_status', methods=['GET'])
def get_ingestion_status():
    try:
        ingestion_status = int(r.get('ingestion_status'))
        
        if ingestion_status == 1:
            return jsonify({'message': 'Ingestion in progress'}), 200
        
        elif ingestion_status == -1:
            return jsonify({'message': 'Ingestion failed'}), 500
        
        else:
            return jsonify({'message': 'No ingestion in progress'}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)