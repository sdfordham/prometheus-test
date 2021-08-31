FROM python:3.8-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV API_KEY=""
ENV BIKEPOINT_ID="BikePoints_73"
ENV SERVER_PORT=8000
ENV REQUEST_BUFFER=10

COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

CMD ["python", "go.py"]
