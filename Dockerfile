FROM python:3.8-alpine

# Copy requirements.txt to the docker image
COPY requirements.txt /app/requirements.txt

WORKDIR /app

# Install psycopg2 dependencies
RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev g++

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the models folder to the docker image
COPY models/ /app/models/

# Copy the app.py file to the docker image
COPY app.py /app/app.py

# Copy the env file to the docker image
COPY .env .

# Run the flask app
ENTRYPOINT [ "python" ]

CMD [ "app.py" ]
