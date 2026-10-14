# Build context is the project root, so we can copy both backend/ and ml/artifacts/
FROM python:3.11-slim

# XGBoost needs this system library on Linux
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Layout inside the container matches the project, because config.py
# finds the models relative to the project root (/app)
WORKDIR /app/backend

# Install packages first (Docker caches this step, so rebuilds are fast)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the API code and BOTH trained models
COPY backend/app ./app
COPY ml/artifacts /app/ml/artifacts

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# Hosts like Render give us a PORT variable; locally it falls back to 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]