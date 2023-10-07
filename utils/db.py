import psycopg2
from psycopg2 import sql

# Connect to default database
db_params = {
    'host': 'localhost',
    'port': '5432',
    'database': 'postgres',
    'user': 'postgres',
    'password': '12345'
}

# Create new database

try:
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    connection.autocommit = True
    new_db = 'neuralworks'
    
    check_db = sql.SQL("SELECT 1 FROM pg_database WHERE datname = {}").format(sql.Literal(new_db))
    cursor.execute(check_db)
    
    if not cursor.fetchone():
        create_db_query = sql.SQL("CREATE DATABASE {}").format(sql.Identifier(new_db))
        cursor.execute(create_db_query)
        print("Database created successfully")  
    else:
        print("Database already exists")
    
    cursor.close()
    connection.close()
    
except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)
    
# Create trip_id_seq sequence

db_params = {
    'host': 'localhost',
    'port': '5432',
    'database': 'neuralworks',
    'user': 'postgres',
    'password': '12345'
}

try:
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    connection.autocommit = True
    
    create_seq_query = '''CREATE SEQUENCE trip_id_seq
            START WITH 1
            INCREMENT BY 1
            NO MINVALUE
            NO MAXVALUE
            CACHE 1; '''
    
    cursor.execute(create_seq_query)
    print("Sequence created successfully in PostgreSQL")
    
    cursor.close()
    connection.close()
    
except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)            

# Create trips table

try:
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    connection.autocommit = True
    
    create_table_query = '''CREATE TABLE trips
            (ID                     SERIAL                  PRIMARY KEY,
            REGION                  TEXT                    NOT NULL,
            ORIGIN_X                NUMERIC                 NOT NULL,
            ORIGIN_Y                NUMERIC                 NOT NULL,
            DESTINATION_X           NUMERIC                 NOT NULL,
            DESTINATION_Y           NUMERIC                 NOT NULL,
            DATETIME                TIMESTAMP               NOT NULL,
            DATASOURCE              TEXT                    NOT NULL); '''
    
    cursor.execute(create_table_query)
    print("Table created successfully in PostgreSQL")
    
    cursor.close()
    connection.close()
    
except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)
    
    
    
    