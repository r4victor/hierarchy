FROM python:3.7

WORKDIR /usr/src/hierarchy

COPY app app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV FLASK_APP="app"

CMD flask run --host=0.0.0.0