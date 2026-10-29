FROM python:3.12.6-slim-bookworm
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py bola_model.py flask_routes.py swagger.json discover.sh ./
COPY static ./static
EXPOSE 80
ENV PORT=80
CMD ["python", "-u", "app.py"]
