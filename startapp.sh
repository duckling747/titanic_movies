#!/bin/sh
flask db upgrade
exec gunicorn titanic_movies:app --bind 0.0.0.0:$PORT -w 3
