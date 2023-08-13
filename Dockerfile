FROM python:3.11.3-slim-buster
LABEL maintainer="lazaryshyn1998@gmail.com"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

CMD ["flask", "run", "-h", "0.0.0.0"]