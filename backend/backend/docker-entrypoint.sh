#!/usr/bin/env bash
set -euo pipefail

JOB_ID="${JOB_ID:-demo_song_01}"
SEED_ON_START="${SEED_ON_START:-true}"
DATA_ROOT="${DATA_ROOT:-/app/data}"
SEEDS_STEMS_DIR="${SEEDS_STEMS_DIR:-/app/seeds/stems}"
SEEDS_META_DIR="${SEEDS_META_DIR:-/app/seeds/meta}"

STEMS_DIR="$DATA_ROOT/stems/$JOB_ID"

if [[ "${SEED_ON_START}" == "true" ]]; then
  if [[ ! -d "$STEMS_DIR" || -z "$(ls -A "$STEMS_DIR" 2>/dev/null || true)" ]]; then
    echo "[entrypoint] Seeding WebDAW data for job '$JOB_ID' into $DATA_ROOT …"
    python /app/scripts/seed_webdaw.py \
      --job-id "$JOB_ID" \
      --stems "$SEEDS_STEMS_DIR" \
      --meta "$SEEDS_META_DIR" \
      --data-root "$DATA_ROOT"
  else
    echo "[entrypoint] Seed skipped — stems already exist at $STEMS_DIR"
  fi
else
  echo "[entrypoint] SEED_ON_START=false — skipping seed"
fi

exec "$@"
