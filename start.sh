envsubst '$PORT' < /app/vhost.conf > /etc/nginx/conf.d/default.conf;

streamlit run /app/frontend/app.py --server.address=0.0.0.0 \
--client.toolbarMode=minimal --client.showErrorDetails=false \
& uvicorn main:app --host=0.0.0.0 \
& nginx -g "daemon off;"
