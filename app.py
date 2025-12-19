from flask import Flask, render_template, request, redirect, url_for
from db import get_db_connection
import uuid
from datetime import date

app = Flask(__name__)

# -------------------------
# Home page – random 20 movies
# -------------------------
@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT movie_id, title, poster_path
        FROM movie_project.Movies
        ORDER BY RANDOM()
        LIMIT 20
    """)
    movies = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("index.html", movies=movies)

# -------------------------
# Movie detail page
# -------------------------
@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    conn = get_db_connection()
    cur = conn.cursor()

    # Movie info
    cur.execute("""
        SELECT title, release_year, description, average_rating, poster_path
        FROM movie_project.Movies
        WHERE movie_id = %s
    """, (movie_id,))
    movie = cur.fetchone()

    # Genres
    cur.execute("""
        SELECT g.name
        FROM movie_project.Genres g
        JOIN movie_project.MovieGenres mg ON g.genre_id = mg.genre_id
        WHERE mg.movie_id = %s
    """, (movie_id,))
    genres = [g[0] for g in cur.fetchall()]

    # Cast
    cur.execute("""
        SELECT a.actor_id, a.name, a.profile_path
        FROM movie_project.Actors a
        JOIN movie_project.Stars s ON a.actor_id = s.actor_id
        WHERE s.movie_id = %s
    """, (movie_id,))
    cast = cur.fetchall()

    # Reviews
    cur.execute("""
        SELECT user_name, rating, review_text, time_created
        FROM movie_project.Reviews
        WHERE movie_id = %s
        ORDER BY time_created DESC
    """, (movie_id,))
    reviews = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "movie.html",
        movie=movie,
        genres=genres,
        cast=cast,
        reviews=reviews,
        movie_id=movie_id
    )

# -------------------------
# Search movies
# -------------------------
@app.route("/search")
def search():
    query = request.args.get("q", "")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT movie_id, title, poster_path
        FROM movie_project.Movies
        WHERE LOWER(title) LIKE LOWER(%s)
        LIMIT 20
    """, (f"%{query}%",))

    movies = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("index.html", movies=movies, search=query)

# -------------------------
# Add review
# -------------------------
@app.route("/add_review", methods=["POST"])
def add_review():
    movie_id = request.form["movie_id"]
    user_name = request.form["user_name"]
    rating = int(request.form["rating"])
    review_text = request.form["review_text"]

    review_id = str(uuid.uuid4())

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO movie_project.Reviews (review_id, user_name, movie_id, time_created, rating, review_text)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (review_id, user_name, movie_id, date.today(), rating, review_text))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("movie_detail", movie_id=movie_id))

@app.route("/actor/<int:actor_id>")
def actor_detail(actor_id):
    conn = get_db_connection()
    cur = conn.cursor()

    # Actor info
    cur.execute("""
        SELECT name, date_of_birth, biography, profile_path
        FROM movie_project.Actors
        WHERE actor_id = %s
    """, (actor_id,))
    actor = cur.fetchone()

    # Movies this actor starred in
    cur.execute("""
        SELECT m.movie_id, m.title, m.poster_path
        FROM movie_project.Movies m
        JOIN movie_project.Stars s ON m.movie_id = s.movie_id
        WHERE s.actor_id = %s
    """, (actor_id,))
    movies = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "actor.html",
        actor=actor,
        movies=movies
    )


if __name__ == "__main__":
    app.run(port=8000, debug=True)
