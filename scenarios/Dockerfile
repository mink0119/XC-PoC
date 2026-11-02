# Attacker / learn-traffic lab UI (static + tiny Python server)
# Separate from Pet Shop API — expose on host :8765
FROM python:3.12.6-slim-bookworm
WORKDIR /app
COPY serve_lab.py ./
COPY lab ./lab
ENV LAB_HOST=0.0.0.0
ENV LAB_PORT=8765
EXPOSE 8765
CMD ["python", "-u", "serve_lab.py", "--host", "0.0.0.0", "--port", "8765", "--no-open"]
