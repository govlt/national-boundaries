#!/bin/sh

gunicorn --bind 0.0.0.0:80 --workers "${WORKERS}" -k workers.ApiWorker main:app