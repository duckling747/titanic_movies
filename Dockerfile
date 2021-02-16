FROM python:alpine
WORKDIR /app
COPY ./migrations ./migrations
COPY ./app ./app
COPY requirements.txt startapp.sh titanic_movies.py ./
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    python3-dev \
    musl-dev \
    postgresql-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del --no-cache .build-deps \
    && adduser -D app \
    && apk add --no-cache postgresql-libs \
    && chown -R app /app \
    && chmod +x /app/startapp.sh \
    && rm -f /sbin/apk \
    && rm -rf /etc/apk \
    && rm -rf /lib/apk \
    && rm -rf /usr/share/apk \
    && rm -rf /var/lib/apk 
USER app
ENV FLASK_APP="titanic_movies.py"
ENV FLASK_ENV="production"
ENTRYPOINT ["./startapp.sh"]
