web: gunicorn swiftloan.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A swiftloan worker --loglevel=info
beat: celery -A swiftloan beat --loglevel=info
