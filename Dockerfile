FROM python:3.9-slim-buster

RUN apt-get update && apt-get install -y netcat

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY . /app
WORKDIR /app

EXPOSE 80

CMD ["sh", "-c", "python -m server $PORT"]
