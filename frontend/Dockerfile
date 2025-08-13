FROM python:3.12
ENV PYTHONUNBUFFERED=1
RUN mkdir /app
WORKDIR /app/frontend
COPY ./requirements.txt /app/frontend/requirements.txt
COPY ./app.py /app/frontend/app.py
COPY ./.streamlit/ /app/frontend/.streamlit/
COPY ./__init__.py /app/frontend/__init__.py/
RUN pip install -r /app/frontend/requirements.txt
