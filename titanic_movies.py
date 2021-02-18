from app import init_app
from os import environ

app = init_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=environ.get('PORT') or 80)
