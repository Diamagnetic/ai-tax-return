FROM python:3.12
ENV PYTHONUNBUFFERED=1
RUN mkdir /app
RUN mkdir /app/backend
WORKDIR /app/backend
COPY ./requirements.txt /app/backend/requirements.txt
COPY ./main.py /app/backend/main.py
COPY ./__init__.py /app/backend/__init__.py
COPY ./static/templates/f1040_2024.pdf /app/backend/static/templates/f1040_2024.pdf
COPY ./api/ /app/backend/api/
COPY ./core/ /app/backend/core/
COPY ./models/ /app/backend/models/
COPY ./services/ /app/backend/services/
COPY ./tax_policy/ /app/backend/tax_policy/
RUN pip install -r /app/backend/requirements.txt
