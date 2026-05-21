#!/bin/sh
set -e

echo "Waiting for database..."
python wait-for-db.py

if [ $# -gt 0 ]; then
    exec python main.py "$@"
else
    exec python main.py server
fi