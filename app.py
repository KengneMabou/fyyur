#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import datetime as dt
import json
import dateutil.parser
import babel
import sys
from flask import render_template, request, Response, flash, redirect, url_for, abort, jsonify
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from app_bootstrapping import db, app, moment, migrate
from forms import ShowForm, VenueForm, ArtistForm
from models import Artist, Venue, Show
from sqlalchemy import or_

#----------------------------------------------------------------------------#
# App Config: See app_bootstrapping.py
#----------------------------------------------------------------------------#

# connect to a local postgresql database
# See config.py file

#----------------------------------------------------------------------------#
# Models. See models.py file
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    try:
        date = dateutil.parser.parse(value)
        if format == 'full':
            format="EEEE MMMM, d, y 'at' h:mma"
        elif format == 'medium':
            format="EE MM, dd, y h:mma"
        return babel.dates.format_datetime(date, format, locale='en')
    except:
        pass

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    recent_artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()
    recent_venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
    return render_template('pages/home.html',recent_artists=recent_artists, recent_venues=recent_venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # Replace with real venues data.
    # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    data = list()
    city_state_mapping = {}
    all_venues = Venue.query.all()
    # print(all_venues)
    venue_order = 0
    venue_number = None
    for c_venue in all_venues:
        venue_key = '%s-%s' % (c_venue.state, c_venue.city)
        tot_shows_per_venue = Show.query.filter_by(venue_id=c_venue.id).count()
        venue_to_append = {'id': c_venue.id,
                           'name': c_venue.name,
                           'num_upcoming_shows':tot_shows_per_venue,
                           }

        if venue_key in city_state_mapping:
            venue_number = city_state_mapping[venue_key]
            data[venue_number]['venues'].append(venue_to_append)
        else:
            city_state_mapping[venue_key] = venue_order
            venue_order = venue_order + 1
            data.append({'city':c_venue.city,
                         'state': c_venue.state,
                         'venues': [venue_to_append]
                         })

    #
    return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # Implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    result = Venue.query.filter(or_(Venue.name.ilike(f"%{request.form.get('search_term','')}%"),
                                    Venue.city.ilike(f"%{request.form.get('search_term', '')}%"),
                                    Venue.state.ilike(f"%{request.form.get('search_term', '')}%"),
                                    ))
    response = {
        'count':result.count(),
        'data': [{'id': q_res.id,
                  'name': q_res.name,
                  'num_upcoming_shows': Show.query.filter(Show.venue_id == q_res.id, Show.start_time >= dt.datetime.today()).count()
                } for q_res in result],
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id

    error = False
    data = None
    try:
        the_venue = Venue.query.get(venue_id)
        past_shows = Show.query.filter(Show.venue_id==venue_id, Show.start_time < dt.datetime.today())
        next_shows = Show.query.filter(Show.venue_id == venue_id, Show.start_time >= dt.datetime.today())
        data = {
            "id": the_venue.id,
            "name": the_venue.name,
            "genres": the_venue.genres.split(','),
            "address": the_venue.address,
            "city": the_venue.city,
            "state": the_venue.state,
            "phone": the_venue.phone,
            "website": the_venue.website_link,
            "facebook_link": the_venue.facebook_link,
            "seeking_talent": the_venue.seeking_talent,
            "image_link": the_venue.image_link,
            "past_shows": [{'artist_id':p_sh.artist.id,
                            'artist_name':p_sh.artist.name,
                            'artist_image_link':p_sh.artist.image_link,
                            'start_time': str(p_sh.start_time),
                            } for p_sh in past_shows],

            'upcoming_shows': [{'artist_id':n_sh.artist.id,
                            'artist_name':n_sh.artist.name,
                            'artist_image_link':n_sh.artist.image_link,
                            'start_time': str(n_sh.start_time),
                            } for n_sh in next_shows],
            'past_shows_count': past_shows.count(),
            'upcoming_shows_count':next_shows.count(),
        }
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred: Error during db reading. Venue could not be displayed.', 'error')
            return redirect(url_for('venues'))
            # abort(404)
        else:
            flash('Venue ' + the_venue.name + ' was successfully displayed!')
            # return redirect(url_for('shows'))
            # return render_template('pages/home.html')
            # return redirect(url_for('index'))
            return render_template('pages/show_venue.html', venue=data)

    # data3={
    #     "id": 3,
    #     "name": "Park Square Live Music & Coffee",
    #     "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    #     "address": "34 Whiskey Moore Ave",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "415-000-1234",
    #     "website": "https://www.parksquarelivemusicandcoffee.com",
    #     "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "past_shows": [{
    #         "artist_id": 5,
    #         "artist_name": "Matt Quevedo",
    #         "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #         "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [{
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 1,
    # }

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # Insert form data as a new Venue record in the db, instead
    # modify data to be the data object returned from db insertion
    form = VenueForm()
    if form.validate_on_submit():
        # on successful db insert, flash success
        error = False
        venue_data = {}
        try:
            new_venue = Venue(name=form.name.data, city=form.city.data, state=form.state.data,
                              address =form.address.data, phone =form.phone.data, genres =form.genres.data,
                              facebook_link =form.facebook_link.data, image_link =form.image_link.data,
                              website_link =form.website_link.data, seeking_talent = form.seeking_talent.data,
                              seeking_description =form.seeking_description.data)

            db.session.add(new_venue)
            db.session.commit()
            venue_data['name'] = new_venue.name
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
            if error:
                flash('An error occurred: Error during db insertion. Venue '
                      + form.name.data + ' could not be listed.', 'error')
                return render_template('forms/new_venue.html', form=form)
                # return redirect(url_for('venues'))
                # abort(400)
            else:
                flash('Venue ' + venue_data['name'] + ' was successfully listed!')
                # return redirect(url_for('venues'))
                # return render_template('pages/home.html')
                return redirect(url_for('index'))
    else:
        # For unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred: Your form is invalid. Venue ' +
              form.name.data + ' could not be listed.', 'error')
        return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    error = False
    venue_data = {}
    try:
        venue = Venue.query.get(venue_id)
        venue_data['name'] = venue.name
        venue_data['js_redirect'] = url_for('index')
        db.session.delete(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred: Error during db deletion. Venue '
                  + venue_data['name'] + ' could not be deleted.', 'error')
            return redirect(url_for('venues'))
            # abort(400)
        else:
            flash('Venue ' + venue_data['name'] + ' was successfully deleted!')
            # return redirect(url_for('venues'))
            # return render_template('pages/home.html')
            # return redirect(url_for('index'))
            return jsonify(venue_data)

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # Replace with real data returned from querying the database
    data = list()
    all_artists = Artist.query.all()
    for c_artist in all_artists:
        data.append({'id':c_artist.id,
                     'name': c_artist.name,
                     })

    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # Implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    result = Artist.query.filter(or_(Artist.name.ilike(f"%{request.form.get('search_term', '')}%"),
                                     Artist.city.ilike(f"%{request.form.get('search_term', '')}%"),
                                     Artist.state.ilike(f"%{request.form.get('search_term', '')}%")
                                     ))
    response = {
        'count': result.count(),
        'data': [{'id': q_res.id,
                  'name': q_res.name,
                  'num_upcoming_shows': Show.query.filter(Show.artist_id == q_res.id,
                                                          Show.start_time >= dt.datetime.today()).count()
                  } for q_res in result],
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    error = False
    data = None
    try:
        the_artist = Artist.query.get(artist_id)
        past_shows = Show.query.filter(Show.artist_id == artist_id, Show.start_time < dt.datetime.today())
        next_shows = Show.query.filter(Show.artist_id == artist_id, Show.start_time >= dt.datetime.today())
        data = {
            "id": the_artist.id,
            "name": the_artist.name,
            "genres": the_artist.genres.split(','),
            "city": the_artist.city,
            "state": the_artist.state,
            "phone": the_artist.phone,
            "website": the_artist.website_link,
            "facebook_link": the_artist.facebook_link,
            "seeking_venue": the_artist.seeking_venue,
            "image_link": the_artist.image_link,
            "available_start_time": str(the_artist.available_start_time),
            "available_end_time": str(the_artist.available_end_time),
            "past_shows": [{'venue_id': p_sh.venue.id,
                            'venue_name': p_sh.venue.name,
                            'venue_image_link': p_sh.venue.image_link,
                            'start_time': str(p_sh.start_time),
                            } for p_sh in past_shows],

            'upcoming_shows': [{'venue_id': n_sh.venue.id,
                                'venue_name': n_sh.venue.name,
                                'venue_image_link': n_sh.venue.image_link,
                                'start_time': str(n_sh.start_time),
                                } for n_sh in next_shows],
            'past_shows_count': past_shows.count(),
            'upcoming_shows_count': next_shows.count(),
        }
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred: Error during db reading. Artist could not be displayed.', 'error')
            return redirect(url_for('artists'))
            # abort(404)
        else:
            flash('Artist ' + the_artist.name + ' was successfully displayed!')
            # return redirect(url_for('shows'))
            # return render_template('pages/home.html')
            # return redirect(url_for('index'))
            return render_template('pages/show_artist.html', artist=data)
    # data1={
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "past_shows": [{
    #         "venue_id": 1,
    #         "venue_name": "The Musical Hop",
    #         "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #         "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    error=False
    artist = None
    form = None
    try:
        the_artist = Artist.query.get(artist_id)
        artist={
            "id": the_artist.id,
            "name": the_artist.name,
            "genres": the_artist.genres.split('-'),
            "city": the_artist.city,
            "state": the_artist.state,
            "phone": the_artist.phone,
            "website": the_artist.website_link,
            "facebook_link": the_artist.facebook_link,
            "seeking_venue": the_artist.seeking_venue,
            "seeking_description": the_artist.seeking_description,
            "image_link": the_artist.image_link,
        }
        form = ArtistForm(obj=the_artist)
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred: Error during db reading. Artist could not be displayed.', 'error')
            return redirect(url_for('artists'))
            # abort(404)
        else:
            flash('Artist ' + the_artist.name + ' was successfully displayed!')
            # return redirect(url_for('shows'))
            # return render_template('pages/home.html')
            # return redirect(url_for('index'))
            return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # Take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    error = False
    form = ArtistForm(formdata=request.form)
    bad_availability = False
    try:
        the_artist = Artist.query.get(artist_id)
        artist = {
            "id": the_artist.id,
            "name": the_artist.name,
            "genres": the_artist.genres.split('-'),
            "city": the_artist.city,
            "state": the_artist.state,
            "phone": the_artist.phone,
            "website": the_artist.website_link,
            "facebook_link": the_artist.facebook_link,
            "seeking_venue": the_artist.seeking_venue,
            "seeking_description": the_artist.seeking_description,
            "image_link": the_artist.image_link,
        }
        if form.validate_on_submit():
            the_artist.name = form.name.data
            the_artist.genres = form.genres.data
            the_artist.city = form.city.data
            the_artist.state = form.state.data
            the_artist.phone = form.phone.data
            the_artist.website_link = form.website_link.data
            the_artist.facebook_link = form.facebook_link.data
            the_artist.seeking_venue = form.seeking_venue.data
            the_artist.seeking_description = form.seeking_description.data
            the_artist.image_link = form.image_link.data
            the_artist.available_start_time = form.available_start_time.data
            the_artist.available_end_time = form.available_end_time.data
            if the_artist.is_period_validity_incorrect():
                bad_availability = True
                raise Exception('Bad availability format')
            db.session.commit()
        else:
            flash('An error occurred: Your form is invalid. Artist ' +
                  the_artist.name + ' could not be updated.', 'error')
            return render_template('forms/edit_artist.html', form=form, artist=artist)
            # return redirect(url_for('edit_artist', artist_id=artist_id))
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred: Error during db updating. Artist could not be updated.', 'error')
            if bad_availability:
                flash('An error occurred: The availability period is not correcty set', 'error')
            return redirect(url_for('artists'))
            # abort(404)
        else:
            flash('Artist ' + form.name.data + ' was successfully updated!')
            # return redirect(url_for('shows'))
            # return render_template('pages/home.html')
            # return redirect(url_for('index'))
            return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    error = False
    venue = None
    form = None
    try:
        the_venue = Venue.query.get(venue_id)
        venue = {
            "id": the_venue.id,
            "name": the_venue.name,
            "genres": the_venue.genres.split('-'),
            "address": the_venue.address,
            "city": the_venue.city,
            "state": the_venue.state,
            "phone": the_venue.phone,
            "website": the_venue.website_link,
            "facebook_link": the_venue.facebook_link,
            "seeking_talent": the_venue.seeking_talent,
            "seeking_description": the_venue.seeking_description,
            "image_link": the_venue.image_link,
        }
        form = VenueForm(obj=the_venue)
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred: Error during db reading. Venue could not be displayed.', 'error')
            return redirect(url_for('venues'))
            # abort(404)
        else:
            flash('Venue ' + the_venue.name + ' was successfully displayed!')
            # return redirect(url_for('shows'))
            # return render_template('pages/home.html')
            # return redirect(url_for('index'))
            return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    #Take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    error = False
    form = VenueForm(formdata=request.form)
    try:
        the_venue = Venue.query.get(venue_id)
        venue = {
            "id": the_venue.id,
            "name": the_venue.name,
            "genres": the_venue.genres.split('-'),
            "city": the_venue.city,
            "state": the_venue.state,
            "phone": the_venue.phone,
            "address": the_venue.address,
            "website": the_venue.website_link,
            "facebook_link": the_venue.facebook_link,
            "seeking_talent": the_venue.seeking_talent,
            "seeking_description": the_venue.seeking_description,
            "image_link": the_venue.image_link,
        }
        if form.validate_on_submit():
            the_venue.name = form.name.data
            the_venue.genres = form.genres.data
            the_venue.city = form.city.data
            the_venue.state = form.state.data
            the_venue.phone = form.phone.data
            the_venue.address = form.address.data
            the_venue.website_link = form.website_link.data
            the_venue.facebook_link = form.facebook_link.data
            the_venue.seeking_talent = form.seeking_talent.data
            the_venue.seeking_description = form.seeking_description.data
            the_venue.image_link = form.image_link.data
            db.session.commit()
        else:
            flash('An error occurred: Your form is invalid. Venue ' +
                  the_venue.name + ' could not be updated.', 'error')
            return render_template('forms/edit_venue.html', form=form, venue=venue)
            # return redirect(url_for('edit_venue', venue_id=venue_id))
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred: Error during db updating. Venue could not be updated.', 'error')
            return redirect(url_for('venues'))
            # abort(404)
        else:
            flash('Venue ' + form.name.data + ' was successfully updated!')
            # return redirect(url_for('shows'))
            # return render_template('pages/home.html')
            # return redirect(url_for('index'))
            return redirect(url_for('show_venue', venue_id=venue_id))

    # return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # Insert form data as a new Artist record in the db, instead
    # modify data to be the data object returned from db insertion
    form = ArtistForm()
    bad_availability = False
    if form.validate_on_submit():
        # on successful db insert, flash success
        error = False
        artist_data = {}
        try:
            new_artist = Artist(name=form.name.data, city=form.city.data, state=form.state.data,
                                phone=form.phone.data, genres=form.genres.data,
                                facebook_link=form.facebook_link.data, image_link=form.image_link.data,
                                website_link=form.website_link.data, seeking_venue=form.seeking_venue.data,
                                seeking_description=form.seeking_description.data,
                                available_start_time=form.available_start_time.data,
                                available_end_time=form.available_end_time.data,)

            ## Should put this in ArtistForm's validate method
            if new_artist.is_period_validity_incorrect():
                bad_availability = True
                raise Exception('Bad availabity format')
            ############


            db.session.add(new_artist)
            db.session.commit()
            artist_data['name'] = new_artist.name
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
            if error:
                flash('An error occurred: Error during db insertion. Artist '
                      + form.name.data + ' could not be listed.', 'error')

                if bad_availability:
                    flash('An error occurred: The availability period is not correcty set', 'error')

                return render_template('forms/new_artist.html', form=form)
                # return redirect(url_for('artists'))
                # abort(400)
            else:
                flash('Artist ' + artist_data['name'] + ' was successfully listed!')
                # return redirect(url_for('artists'))
                # return render_template('pages/home.html')
                return redirect(url_for('index'))
    else:
        # On unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred: Your form is invalid. Artist ' +
              form.name.data + ' could not be listed.', 'error')
        return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # Displays list of shows at /shows
    # Replace with real venues data.
    data = list()
    all_shows = Show.query.all()
    for c_show in all_shows:
        data.append({'venue_id': c_show.venue.id,
                     'venue_name': c_show.venue.name,
                     'artist_id': c_show.artist.id,
                     'artist_name': c_show.artist.name,
                     'artist_image_link': c_show.artist.image_link,
                     'start_time': str(c_show.start_time)
                     })
    # data=[{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    # }]
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called upon submitting the new show listing form

    form = ShowForm()
    is_bad_start_time = False
    if form.validate_on_submit():
        # on successful db insert, flash success
        error = False
        show_data = {}
        try:
            the_artist = Artist.query.get(int(form.artist_id.data))
            the_venue = Venue.query.get(int(form.venue_id.data))

            new_show = Show(artist_id=form.artist_id.data, venue_id=form.venue_id.data,
                            start_time=form.start_time.data)

            # We should put this in ShowForm validate method
            if the_artist.available_start_time and new_show.start_time < the_artist.available_start_time:
                is_bad_start_time = True
            if the_artist.available_end_time and new_show.start_time > the_artist.available_end_time:
                is_bad_start_time = True
            if is_bad_start_time:
                raise Exception('Bad start time')

            db.session.add(new_show)
            db.session.commit()
            show_data['desc'] = "Show for artist %s at venue %s on %s" % (the_artist.name,
                                                                          the_venue.name,
                                                                          new_show.start_time)
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
            if error:
                flash('An error occurred: Error during db insertion. Show could not be listed.', 'error')
                if is_bad_start_time:
                    flash('An error occurred: The startime of the show should be in the availability '
                          'period of the artist.', 'error')
                return render_template('forms/new_show.html', form=form)
                # return redirect(url_for('shows'))
                # abort(400)
            else:
                flash('Show ' + show_data['desc'] + ' was successfully listed!')
                # return redirect(url_for('shows'))
                # return render_template('pages/home.html')
                return redirect(url_for('index'))
    else:

        flash('An error occurred: Your form is invalid. Show  could not be listed.', 'error')
        return render_template('forms/new_show.html', form=form)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
