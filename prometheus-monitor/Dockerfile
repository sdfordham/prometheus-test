FROM ubuntu:latest

RUN apt-get update && \
    apt-get install prometheus && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY prometheus.yml .

CMD ["prometheus", "--config.file=prometheus.yml"]
