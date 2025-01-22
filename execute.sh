#!/bin/sh

python apply_migrations.py
python -m flask run --host=0.0.0.0