FROM python:3.7

WORKDIR /usr/src/hierarchy

COPY app app
COPY tests tests
COPY requirements.txt .

# install psycopg2 dependencies
RUN apt-get update && apt-get install -y python3-dev libpq-dev

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "--bind=0.0.0.0:8000", "--workers=2", "app:create_app()"]