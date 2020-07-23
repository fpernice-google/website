from flask.cli import FlaskGroup
from routes.server import app

cli = FlaskGroup(app)

if __name__ == "__main__":
    cli()