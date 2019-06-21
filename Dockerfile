FROM python:3.7

WORKDIR /usr/src/hierarchy

COPY app app
COPY tests tests
COPY requirements.txt .

# install psycopg2 dependencies
RUN apt-get update && apt-get install -y python3-dev libpq-dev

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV FLASK_APP="app"

CMD flask run --host=0.0.0.0