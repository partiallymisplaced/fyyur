#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
