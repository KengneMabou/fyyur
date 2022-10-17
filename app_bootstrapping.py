from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
moment = Moment(app)
from flask_migrate import Migrate

app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)