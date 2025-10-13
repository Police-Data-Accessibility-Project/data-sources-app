#!/bin/sh

gunicorn \
  --worker-tmp-dir /dev/shm \
  --bind 0.0.0.0:8080 \
  -k uvicorn.workers.UvicornWorker \
  'app:create_asgi_app()'