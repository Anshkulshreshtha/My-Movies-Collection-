from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
import sqlite3
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'  # flask csrf secret key
Bootstrap(app)


# themoviedb api key and url endpoints ~
SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
movie_image_url_endpoint = 'https://image.tmdb.org/t/p/w500'
API_KEY = "YOUR TMDB API_KEY"  # my API key


# wtform movie update!
class UpdateForm(FlaskForm):
    rating = FloatField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")


# wtf movie adding form
class FindMovieForm(FlaskForm):
    title = StringField("Movie Title")
    adding = SubmitField("Add Movie")


# CREATE DB
db = sqlite3.connect("MOVIES.db", check_same_thread=False)
cursor = db.cursor()

# After adding the new_movie the code needs to be commented out/deleted.
# So you are not trying to add the same movie twice.
# ------------------------------------
# CREATE TABLE

cursor.execute(
    "CREATE TABLE IF NOT EXISTS MOVIES (id INTEGER PRIMARY KEY AUTOINCREMENT,"
    " title varchar(50) NOT NULL UNIQUE,"
    " year INTEGER NOT NULL,"
    " description varchar(500) NOT NULL,"
    " rating FLOAT NULL,"
    " ranking INTEGER NULL,"
    " review varchar(250) NULL,"
    " img_url varchar(250) NOT NULL) "
)

# inserting value in the database via code! ---------------
# cursor.execute(
#     "INSERT INTO MOVIES VALUES(1, 'Phone Booth', '2002', 'Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.', "
#     "'7.3', '9', 'Best movie of all time', "
#     "'https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg') "
# )
# db.commit()


# all Flask routes below:----------
@app.route("/")
def home():
    MOVIES = cursor.execute("SELECT * FROM MOVIES ORDER BY rating DESC")
    return render_template('index.html', movies=MOVIES)


@app.route("/edit", methods=["GET", "POST"])
def edit_movie():
    form = UpdateForm()
    movie_id = request.args.get("id")
    if form.validate():
        updated_rating = request.form['rating']
        updated_review = request.form['review']
        cursor.execute("UPDATE MOVIES SET rating = ?, review = ? WHERE id = ?", (updated_rating, updated_review, movie_id,))
        db.commit()
        return redirect(url_for('home'))
    MOVIES = cursor.execute("SELECT * FROM MOVIES")
    return render_template('edit.html', form=form, movies=MOVIES)


@app.route("/delete/<int:num>")
def delete(num):
    cursor.execute("DELETE FROM MOVIES WHERE id = ?", (num,))
    db.commit()
    cursor.execute("SELECT * FROM MOVIES")
    return redirect(url_for('home'))


@app.route("/add", methods=['GET', 'POST'])
def add():
    form = FindMovieForm()
    if form.validate():
        movie_title = request.form['title']
        response = requests.get(f'{SEARCH_URL}?api_key={API_KEY}&language=en-US&query={movie_title}')
        data = response.json()['results']
        return render_template('select.html', options=data)
    return render_template('add.html', form=form)


@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f'https://api.themoviedb.org/3/movie/{movie_api_id}?api_key={API_KEY}&language=en-US'
        response = requests.get(movie_api_url)
        data = response.json()
        movie_title = data['title']
        movie_year = data['release_date'].split("-")[0]
        movie_description = data['overview']
        movie_poster_path = data['poster_path']
        movie_image_url = f'{movie_image_url_endpoint}{movie_poster_path}'
        cursor.execute("INSERT INTO MOVIES(title, year, description, img_url) VALUES (?,?,?,?)", (str(movie_title), str(movie_year), str(movie_description), str(movie_image_url)))
        db.commit()
        cursor.execute("SELECT * FROM MOVIES")
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)

db.close()
