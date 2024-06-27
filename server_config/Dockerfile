FROM python:3.11.5 as base

WORKDIR /app

RUN pip install flask

COPY ./server.py /app

ENTRYPOINT ["python", "/app/server.py"]

EXPOSE 5000