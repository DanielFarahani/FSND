#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import config
from flask_migrate import Migrate
from forms import VenueForm, ArtistForm, ShowForm
from datetime import datetime
import sys
from sqlalchemy import func
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)  # db
migrate = Migrate(app, db)

app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
  __tablename__ = 'Venue'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  genres = db.Column(db.ARRAY(db.String(200)))
  seeking_talent = db.Column(db.Boolean)
  seeking_description = db.Column(db.String(500))
  website = db.Column(db.String(120))
  show = db.relationship('Show', backref='venue', lazy=True)

  def upcoming_shows():
    shows = db.session.query(Venue.id, Venue.name).join(Show).filter(Show.start_time > datetime.now).count()

  def past_shows():
    shows = db.session.query(Venue.id, Venue.name).join(Show).filter(Show.start_time < datetime.now).count()

  def __repr__(self):
    return f'<VID: {self.id}, name: {self.name}, state: {self.state}>'

class Artist(db.Model):
  __tablename__ = 'Artist'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.ARRAY(db.String(200)))
  seeking_venue = db.Column(db.Boolean)
  seeking_description = db.Column(db.String(500))
  website = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  show = db.relationship('Show', backref='artist', lazy=True)

  def __repr__(self):
    return f'<AID: {self.id}, name: {self.name}, state: {self.city}>'

class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
  start_time = db.Column(db.DateTime)

  def __repr__(self):
    return f'<SID: {self.id}, VID: {self.venue_id}, AID: {self.artist_id}, time: {self.start_time}>'

# To fully normalise the database, we'd need genre (genre, artist.id), city(name, state, venue.id).
# Maybe aggregation of Venue and Artist into Venues and Artists for as a fact table

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
  data = []
  areas = Venue.query.distinct('city', 'state').all()
  for area in areas:
    venues = Venue.query.filter(Venue.city == area.city, Venue.state == area.state).all()
    record = {
      'city': area.city,
      'state': area.state,
      'venues': [{'id': venue.id, 'name': venue.name, 'num_upcoming_show': venue.upcoming_shows} for venue in venues],
    }
    data.append(record)
  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  response = {}
  data = []
  venues = Venue.query.filter(func.lower(Venue.name).contains(search_term.lower())).all()
  for venue in venues:
    data.append({'id': venue.id, 'name': venue.name, 'num_upcoming_shows': venue.upcoming_shows})
  response['data'] = data
  response['count'] = len(venues)

  return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  data = Venue.query.filter_by(id=venue_id).first().__dict__
  past_shows = db.session.query(Venue, Show, Artist).filter(Venue.id == Show.venue_id).filter(Artist.id == Show.artist_id).filter(Show.start_time < datetime.now()).filter(Venue.id == venue_id).all()
  upcoming_shows = db.session.query(Venue, Show, Artist).filter(Venue.id == Show.venue_id).filter(Artist.id == Show.artist_id).filter(Show.start_time > datetime.now()).filter(Venue.id == venue_id).all()
  data['past_shows'] = [{'artist_id': a.id, 'artist_name': a.name, 'artist_image_link': a.image_link, 'start_time': str(s.start_time)} for (v, s, a) in past_shows]
  data['upcoming_shows'] = [{'artist_id': a.id, 'artist_name': a.name, 'artist_image_link': a.image_link, 'start_time': str(s.start_time)} for (v, s, a) in upcoming_shows]
  data['past_show_count'] = len(data['past_shows'])
  data['upcoming_show_count'] = len(data['upcoming_shows'])

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  venue = request.form.to_dict()  # name, city, state, address, pone, genres, fb link  
  try:
    new_venue = Venue(name=venue['name'], city=venue['city'], state=venue['state'],
                      address=venue['address'], phone=venue['phone'], genres=request.form.getlist('genres'), 
                      facebook_link=venue['facebook_link'])
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')  # on success
  except Exception as e:
    db.session.rollback()
    app.logger.info(e)
    flash('Venue ' + request.form['name'] + ' was not listed, please try again!')  # on fail
  finally:
    db.session.close()

  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue was successfully deleted!')  # on success
  except Exception as e:
    db.session.rollback()
    flash('Venue was not deleted, please try again!')  # on fail
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.with_entities(Artist.id, Artist.name)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  response = {}
  data = []
  artists = Artist.query.filter(func.lower(Artist.name).contains(search_term.lower())).all()
  for artist in artists:
    data.append({'id': artist.id, 'name': artist.name, 'num_upcoming_shows': artist.upcoming_shows})
  response['data'] = data
  response['count'] = len(artists)

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  data = Artist.query.filter_by(id=artist_id).first().__dict__
  past_shows = db.session.query(Venue, Show, Artist).filter(Venue.id == Show.venue_id).filter(Artist.id == Show.artist_id).filter(Show.start_time < datetime.now()).filter(Artist.id == artist_id).all()
  upcoming_shows = db.session.query(Venue, Show, Artist).filter(Venue.id == Show.venue_id).filter(Artist.id == Show.artist_id).filter(Show.start_time > datetime.now()).filter(Artist.id == artist_id).all()
  data['past_shows'] = [{'venue_id': v.id, 'venue_name': v.name, 'venue_image_link': v.image_link, 'start_time': str(s.start_time)} for (v, s, a) in past_shows]
  data['upcoming_shows'] = [{'venue_id': v.id, 'venue_name': v.name, 'venue_image_link': v.image_link, 'start_time': str(s.start_time)} for (v, s, a) in upcoming_shows]
  data['past_show_count'] = len(data['past_shows'])
  data['upcoming_show_count'] = len(data['upcoming_shows'])

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # genres=request.form.getlist('genres')
  form = ArtistForm()
  artist= Artist.query.all()
  # data format => {id, name, gnre, city, state, phone, web, fb, seeking, seek dsc, image}
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue= Venue.query.all()
  # data format => {id, name, genres, address,city,state,phone, web,fb, seeking, seeking desc, image_link}
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  shows = db.session.query(Venue, Show, Artist).filter(Venue.id == Show.venue_id).filter(Artist.id == Show.artist_id).all()
  data = [{'venue_id': v.id, 'venue_name': v.name, 'artist_id': a.id, 'artist_name': a.name, 'artist_image_link': a.image_link, 'start_time': str(s.start_time)} for (v, s, a) in shows]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
