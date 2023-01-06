FROM python:3.10

WORKDIR /app

RUN apt-get -qq update

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . .

EXPOSE 8000