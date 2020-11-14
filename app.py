#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import config
import json
import datetime
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue')

    def __repr__(self):
      return f'''
      -----------------
      id: {self.id} 
      name: {self.name} 
      city: {self.city}
      state: {self.state}
      address: {self.address}
      genres: {self.genres} 
      phone: {self.phone} 
      image_link: {self.image_link} 
      website: {self.website} 
      facebook_link: {self.facebook_link} 
      seeking_talent: {self.seeking_talent} 
      seeking_description: {self.seeking_description} 
      shows: {self.shows}
      ----------------- 
      '''  

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.Text, nullable=False)
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist')

    def __repr__(self):
      return f'''
      -----------------
      id: {self.id} 
      name: {self.name} 
      city: {self.city}
      state: {self.state}
      phone: {self.phone} 
      genres: {self.genres} 
      image_link: {self.image_link} 
      website: {self.website} 
      facebook_link: {self.facebook_link} 
      seeking_venue: {self.seeking_venue} 
      seeking_description: {self.seeking_description} 
      shows: {self.shows}
      ----------------- 
      '''

class Show(db.Model):
  __tablename__ = 'shows'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  start_time = db.Column(db.DateTime)
  
  def __repr__(self):
      return f'''
      +++++++++++++++++
      id: {self.id} 
      venue_id: {self.venue_id}
      artist_id: {self.artist_id}
      start_time: {self.start_time} 
      +++++++++++++++++ 
      '''

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  areas = []
  locations = db.session.query(Venue).distinct(Venue.city, Venue.state).order_by(Venue.state).all()
  venues = db.session.query(Venue.city, Venue.state, Venue.id, Venue.name).order_by(Venue.name).all()
  for location in locations:
    location = {
      "city": location.city,
      "state": location.state,
      "venues": []
      }
    for venue in venues:
      if venue.city == location["city"] and venue.state == location["state"]:
        location["venues"].append({
            "id": venue.id,
            "name": venue.name
        })
    areas.append(location);
  return render_template('pages/venues.html', areas=areas);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  search_result_count = db.session.query(Venue).filter(
      Venue.name.ilike(f'%{search_term}%')).count()
  search_results = db.session.query(Venue).filter(
      Venue.name.ilike(f'%{search_term}%')).all()
  venues = []
  for venue in search_results:
    venue = {
        "id": venue.id,
        "name": venue.name
    }
    venues.append(venue)

  response = {
      "count": search_result_count,
      "data": venues
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  current_time = datetime.now()

  venue = Venue.query.get(venue_id)
  genres = venue.genres.replace('{', '').replace('}', '').replace('\"', '')
  genres = ''.join(genres).split(",")
  venue.genres = genres
  venue.past_shows = []
  venue.upcoming_shows = []
  venue.past_shows_count = db.session.query(Show).filter_by(venue_id=venue_id).filter(Show.start_time <= current_time).join(
      Artist, Show.artist_id == Artist.id).count()
  venue.upcoming_shows_count = db.session.query(Show).filter_by(venue_id=venue_id).filter(Show.start_time > current_time).join(
      Artist, Show.artist_id == Artist.id).count()

  past_shows = db.session.query(Show).filter_by(venue_id=venue_id).filter(Show.start_time <= current_time).join(
      Artist, Show.artist_id == Artist.id).all()
  for show in past_shows:
    show = {
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "artist_id": show.artist.id,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
  venue.past_shows.append(show)

  upcoming_shows = db.session.query(Show).filter_by(venue_id=venue_id).filter(Show.start_time > current_time).join(
      Artist, Show.artist_id == Artist.id).all()
  for show in upcoming_shows:
    show = {
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "artist_id": show.artist.id,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    venue.upcoming_shows.append(show)

    return render_template('pages/show_venue.html', venue=venue)
  #TODO: ERR Handle id not in db

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()
  errors = False
  body = {}

  try:
    response = request.form
    venue = Venue()

    if 'seeking_talent' in response:
      venue.seeking_talent = True
    else:
      venue.seeking_talent = False

    venue.name = response['name']
    venue.address = response['address']
    venue.city = response['city']
    venue.state = response['state']
    venue.phone = response['phone']
    venue.genres = response.getlist('genres')
    venue.image_link = response['image_link']
    venue.website = response['website']
    venue.facebook_link = response['facebook_link']
    venue.seeking_description = response['seeking_description']

    db.session.add(venue)
    db.session.commit()

    body['name'] = venue.name

  except:
    errors = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  if errors:
    abort(400)

  else:
    flash('Venue ' + body['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

  # TODO: ERR on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: 
  # Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
  artists = db.session.query(Artist.id, Artist.name)
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  search_result_count = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).count()
  search_results = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  artists = []
  for artist in search_results:
    artist = {
      "id": artist.id,
      "name": artist.name
    }
    artists.append(artist)
  
  response = {
      "count": search_result_count,
      "data": artists
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>') 
def show_artist(artist_id):
  #TODO: ERR Handle id not in db
  current_time = datetime.now()
  artist = Artist.query.get(artist_id)
  genres = artist.genres.replace('{', '').replace('}', '').replace('\"', '')
  genres = ''.join(genres).split(",")
  artist.genres = genres
  artist.past_shows = []
  artist.upcoming_shows = []
  artist.past_shows_count = db.session.query(Show).filter_by(artist_id=artist_id).filter(Show.start_time <= current_time).join(
      Venue, Show.venue_id == Venue.id).count()
  artist.upcoming_shows_count = db.session.query(Show).filter_by(artist_id=artist_id).filter(Show.start_time > current_time).join(
      Venue, Show.venue_id == Venue.id).count()

  past_shows = db.session.query(Show).filter_by(artist_id=artist_id).filter(Show.start_time <= current_time).join(
       Venue, Show.venue_id == Venue.id).all()
  for show in past_shows:
    show = {
        "venue_name": show.artist.name,
        "venue_image_link": show.artist.image_link,
        "venue_id": show.artist.id,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    artist.past_shows.append(show)

  upcoming_shows = db.session.query(Show).filter_by(artist_id=artist_id).filter(Show.start_time > current_time).join(
      Venue, Show.venue_id == Venue.id).all()
  for show in upcoming_shows:
    show = {
        "venue_name": show.artist.name,
        "venue_image_link": show.artist.image_link,
        "venue_id": show.artist.id,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    artist.upcoming_shows.append(show)

  return render_template('pages/show_artist.html', artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: 
  # populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: 
  # take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: 
  # populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: 
  # take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()
  errors = False
  body = {}

  try:
    response = request.form
    artist = Artist()    
    if 'seeking_venue' in response:
      artist.seeking_venue = True
    else:
      artist.seeking_venue = False

    artist.name = response['name']
    artist.city = response['city']
    artist.state = response['state']
    artist.phone = response['phone']
    artist.genres = response.getlist('genres')
    artist.image_link = response['image_link']
    artist.website = response['website']
    artist.facebook_link = response['facebook_link']
    artist.seeking_description = response['seeking_description']
    
    db.session.add(artist)
    db.session.commit()

    body['name'] = artist.name
  
  except:
    errors = True
    db.session.rollback()
    print(sys.exc_info())
  
  finally:
    db.session.close()

  if errors:
    abort(400)
  
  else:
    flash('Artist ' + body['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

  # TODO: ERR on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  shows = db.session.query(Show).join(Venue, Show.venue_id == Venue.id).join(Artist, Show.artist_id == Artist.id).all()
  for show in shows:
    show = {
      "id": show.id,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    data.append(show)
    
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm()
  errors = False

  try:
    response = request.form
    show = Show()

    show.artist_id = response['artist_id']
    show.venue_id = response['venue_id']
    show.start_time = response['start_time']

    db.session.add(show)
    db.session.commit()

  except:
    errors = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  if errors:
    abort(400)

  else:
    flash('Show was successfully listed!')
    return render_template('pages/home.html')

  # TODO: ERR on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

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
