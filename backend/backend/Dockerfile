FROM python:3.11-slim

# Install system dependencies for ffmpeg and rubberband-cli
RUN apt-get update && apt-get install -y ffmpeg rubberband-cli curl && rm -rf /var/lib/apt/lists/*

# Create data directories
RUN mkdir -p /app/data/stems /app/data/stretched /app/data/meta

# Install Python dependencies
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code, seed scripts, and seeds
COPY backend/ /app/
COPY scripts/ /app/scripts/
COPY seeds/ /app/seeds/

# Defaults (override in compose)
ENV DATA_STEMS_DIR=/app/data/stems \
    DATA_STRETCHED_DIR=/app/data/stretched \
    DATA_META_DIR=/app/data/meta \
    JOB_ID=demo_song_01 \
    SEED_ON_START=true \
    DATA_ROOT=/app/data \
    SEEDS_STEMS_DIR=/app/seeds/stems \
    SEEDS_META_DIR=/app/seeds/meta

COPY backend/docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uvicorn", "drumtrackai_fastapi_server:app", "--host", "0.0.0.0", "--port", "8000"]
