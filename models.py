import datetime
from app_bootstrapping import db

class Venue(db.Model):

    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(), nullable=False)
    facebook_link = db.Column(db.String(200))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(), nullable=False)
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):

    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(), nullable=False)
    facebook_link = db.Column(db.String(200))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(), nullable=False)
    shows = db.relationship('Show', backref='artist', lazy=True)
    available_start_time = db.Column(db.DateTime, nullable=True, default=datetime.datetime.today())
    available_end_time = db.Column(db.DateTime, nullable=True, default=datetime.datetime.today())

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

    def is_period_validity_incorrect(self):
        bad_availability_format = False
        if self.available_end_time and not self.available_start_time:
            bad_availability_format = True
        if self.available_start_time and self.available_end_time \
                and self.available_end_time < self.available_start_time:
            bad_availability_format = True
        return bad_availability_format

    # Implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)

    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.today())

# Implement Show and Artist models, and complete all model relationships and properties, as a database migration.