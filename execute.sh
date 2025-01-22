#!/bin/sh

python apply_migrations.py
gunicorn --worker-tmp-dir /dev/shm --bind 0.0.0.0:8080 'app:create_app()'