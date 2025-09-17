FROM python:3.12
ENV PYTHONUNBUFFERED=1
RUN mkdir /app

# Frontend
WORKDIR /app/frontend
COPY ./frontend/requirements.txt /app/frontend/requirements.txt
COPY ./frontend/app.py /app/frontend/app.py
COPY ./frontend/api_client.py /app/frontend/api_client.py
COPY ./frontend/user_pii_model.py /app/frontend/user_pii_model.py
COPY ./frontend/config.py /app/frontend/config.py
COPY ./frontend/.streamlit/ /app/frontend/.streamlit/
COPY ./frontend/__init__.py /app/frontend/__init__.py/
RUN pip install -r /app/frontend/requirements.txt

# Backend
RUN mkdir /app/backend
WORKDIR /app/backend
COPY ./backend/requirements.txt /app/backend/requirements.txt
COPY ./backend/main.py /app/backend/main.py
COPY ./backend/__init__.py /app/backend/__init__.py
COPY ./backend/static/templates/f1040_2024.pdf \
     /app/backend/static/templates/f1040_2024.pdf
COPY ./backend/api/ /app/backend/api/
COPY ./backend/core/ /app/backend/core/
COPY ./backend/models/ /app/backend/models/
COPY ./backend/services/ /app/backend/services/
COPY ./backend/tax_policy/ /app/backend/tax_policy/
RUN pip install -r /app/backend/requirements.txt

# Nginx
RUN apt update \
    && apt install --no-install-recommends --no-install-suggests -y nginx \
    && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /etc/nginx/conf.d
RUN rm -f /etc/nginx/sites-enabled/default
COPY ./nginx/vhost.conf /app/vhost.conf

CMD sed "s/\${PORT}/$PORT/g" /app/vhost.conf > /etc/nginx/conf.d/default.conf \
    && cat /etc/nginx/conf.d/default.conf \
    && streamlit run /app/frontend/app.py --server.address=0.0.0.0 \
    --client.toolbarMode=minimal --client.showErrorDetails=false \
    & uvicorn main:app --host=0.0.0.0 \
    & nginx -g "daemon off;"
