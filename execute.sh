#!/bin/sh

gunicorn --worker-tmp-dir /dev/shm --bind 0.0.0.0:8080 'app:create_app()'