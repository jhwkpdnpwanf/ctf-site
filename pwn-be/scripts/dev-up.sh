#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../deploy"
docker compose -f docker-compose.dev.yml up --build