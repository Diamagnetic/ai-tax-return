FROM python:3.12
ENV PYTHONUNBUFFERED=1
RUN mkdir /app
WORKDIR /app
RUN mkdir /app/backend
COPY ./backend/requirements.txt /app/backend/requirements.txt
COPY ./backend/main.py /app/backend/main.py
COPY ./backend/__init__.py /app/backend/__init__.py
COPY ./backend/static/templates/f1040_2024.pdf /app/backend/static/templates/f1040_2024.pdf
COPY ./backend/api/ /app/backend/api/
COPY ./backend/models/ /app/backend/models/
COPY ./backend/services/ /app/backend/services/
COPY ./backend/tax_policy/ /app/backend/tax_policy/
RUN pip install -r /app/backend/requirements.txt
