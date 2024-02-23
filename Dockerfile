FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /src
WORKDIR /src

COPY requirements.txt /src

RUN apt-get update && apt-get install -y git
RUN pip install -r requirements.txt

COPY . /src

EXPOSE 8081

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["sh", "entrypoint.sh"]