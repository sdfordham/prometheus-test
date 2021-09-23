FROM python:3.8-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV API_KEY=""
ENV BIKEPOINT_ID="BikePoints_73"
ENV SERVER_PORT=8000
ENV REQUEST_BUFFER=10

WORKDIR /app
COPY . /app
RUN python -m pip install -r requirements.txt

CMD ["python", "go.py"]
