FROM python:alpine
WORKDIR /app
COPY . .
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    python3-dev \
    musl-dev \
    postgresql-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del --no-cache .build-deps
ENV FLASK_APP="titanic_movies.py"
ENV FLASK_ENV="development"
EXPOSE 80
RUN apk add --no-cache postgresql-libs
ENTRYPOINT ["python", "titanic_movies.py"]
