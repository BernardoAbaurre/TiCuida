# 1) Compila o front-end Vue
FROM node:22-alpine AS front
WORKDIR /front
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# 2) API Flask servindo a API e o front compilado
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL=sqlite:////app/data/ticuida.db \
    LOG_DIR=/app/logs

COPY pyproject.toml README.md ./
COPY ticuida/ ticuida/
RUN pip install --no-cache-dir . gunicorn

COPY migrations/ migrations/
COPY app.py wsgi.py docker-entrypoint.sh ./
COPY --from=front /front/dist frontend/dist
RUN mkdir -p /app/data /app/logs && chmod +x docker-entrypoint.sh

EXPOSE 8000
CMD ["./docker-entrypoint.sh"]
