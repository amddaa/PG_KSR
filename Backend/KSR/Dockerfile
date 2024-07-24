FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -U python-dotenv==1.0.1
RUN pip install -U psycopg2-binary==2.9.9

COPY . /app/

EXPOSE 8000