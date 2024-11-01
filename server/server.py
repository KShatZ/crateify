from os import getenv

from app import create_app

DEBUG_MODE = getenv("DEBUG_MODE", True)
app = create_app()

if __name__ == "__main__":
    app.run(host='localhost', debug=DEBUG_MODE)
