FROM python:3.9
ENV PYTHONUNBUFFERED 1
WORKDIR /accounts
COPY requirements.txt /accounts/requirements.txt
RUN pip install -r requirements.txt
COPY . /accounts