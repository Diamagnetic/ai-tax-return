FROM python:3.12
ENV PYTHONUNBUFFERED=1
RUN mkdir /app
WORKDIR /app/frontend
COPY ./requirements.txt /app/frontend/requirements.txt
COPY ./app.py /app/frontend/app.py
RUN pip install -r /app/frontend/requirements.txt
