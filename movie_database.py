import psycopg2
from datetime import datetime
import requests

movie_list_base_url = "https://api.themoviedb.org/3/movie/now_playing?language=en-US&page="

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwNjM4Y2RjNzcxMzcyNTljOWZlY2NlMzMwNWVlNGQwYiIsIm5iZiI6MTc2NTUwMzY2NC4wNjgsInN1YiI6IjY5M2I3MmIwMjNjZDMyNjYxYWFjOWJlMiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.M7wjOjXxWKdasVl1f1lO4giPe94ShAAXxAvYxf_Pq-0"
}

movie_ids = []

for i in range(20):
    url = movie_list_base_url + str(i+1)
    response = requests.get(url, headers=headers)

    for r in response.json()['results']:
        movie_ids.append(r['id'])
    
    print("page", i + 1)

movies_details = []
movie_genres_list = []
genres = {}
actors_details = {}
movies_actors_list = []
review_list = []

for i, movie_id in enumerate(movie_ids):
    # Get movie detail data

    movie_detail_url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
    movie_detail_response = requests.get(movie_detail_url, headers=headers)
    movie = [
        movie_detail_response.json()['id'],
        movie_detail_response.json()['original_title'],
        int(movie_detail_response.json()['release_date'][:4]),
        movie_detail_response.json()['overview'],
        movie_detail_response.json()['vote_average'],
        movie_detail_response.json()['poster_path']
    ]
    movies_details.append(movie)

    movie_genres = movie_detail_response.json()['genres']

    for movie_genre in movie_genres:
        movie_genres_list.append([movie_genre['id'], movie_id])

        if movie_genre['id'] not in genres:
            genres[movie_genre['id']] = movie_genre['name']

    movie_actor_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?language=en-US"
    movie_actor_response = requests.get(movie_actor_url, headers=headers)

    for actor in movie_actor_response.json()['cast']:
        actor_id = actor['id']
        movies_actors_list.append([actor_id, movie_id])

        actors_details_urls = f"https://api.themoviedb.org/3/person/{actor_id}?language=en-US"
        actor_response = requests.get(actors_details_urls, headers=headers)
        
        if actor_id not in actors_details:
            actors_details[actor_id] = [
                actor_response.json()['id'],
                actor_response.json()['name'],
                actor_response.json()['birthday'],
                actor_response.json()['biography'],
                actor_response.json()['profile_path']
            ]
    
    review_url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews?language=en-US&page=1"
    review_response = requests.get(review_url, headers=headers)

    for review in review_response.json()['results']:
        review_id = review['id']
        review_list.append(
            [
                review['id'],
                review['author'],
                movie_id,
                review['created_at'][:10],
                review['author_details']['rating'] if review['author_details']['rating'] else 0,
                review['content'],
            ]
        )
    
    print(f"{i + 1}/400")

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "YOUR PASSWORD",
    "host": "localhost",
    "port": "5432"
}

GENRES = [[k, v] for k, v in genres.items()]

ACTORS = actors_details.values()

MOVIES = movies_details

REVIEWS = review_list

STARS = movies_actors_list

MOVIEGENRES = movie_genres_list

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

try:
    # ---------- INSERT GENRES ----------
    for genre_id, name in GENRES:
        cur.execute(
            """
                INSERT INTO movie_project.Genres (genre_id, name)
                VALUES (%s, %s)
                ON CONFLICT (genre_id) DO UPDATE
                SET name = EXCLUDED.name
                RETURNING genre_id
            """,
            (genre_id, name)
        )

    conn.commit()
    print("finish genres")

    # ---------- INSERT ACTORS ----------
    for actor_id, name, dob_str, bio, profile_path in ACTORS:
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if (dob_str) else None

        cur.execute(
            """
            INSERT INTO movie_project.Actors (actor_id, name, date_of_birth, biography, profile_path)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (actor_id) DO UPDATE
                SET name = EXCLUDED.name,
                    date_of_birth = EXCLUDED.date_of_birth,
                    biography = EXCLUDED.biography,
                    profile_path = EXCLUDED.profile_path
            RETURNING actor_id
            """,
            (actor_id, name, dob, bio, f"https://image.tmdb.org/t/p/w500{profile_path}")
        )

    conn.commit()
    print("finish actors")

    # ---------- INSERT MOVIES ----------
    for movie_id, title, year, description, average_rating, poster_path in MOVIES:
        cur.execute(
            """
            INSERT INTO movie_project.Movies (movie_id, title, release_year, description, average_rating, poster_path)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (movie_id) DO UPDATE
                SET title = EXCLUDED.title,
                    release_year = EXCLUDED.release_year,
                    description = EXCLUDED.description,
                    average_rating = EXCLUDED.average_rating,
                    poster_path = EXCLUDED.poster_path
            RETURNING movie_id
            """,
            (movie_id, title, year, description, average_rating, f"https://image.tmdb.org/t/p/w500{poster_path}")
        )

    conn.commit()
    print("finish movies")

    # ---------- ASSIGN GENRES TO MOVIES ----------
    for genre_id, movie_id in MOVIEGENRES:
        cur.execute(
            """
            INSERT INTO movie_project.MovieGenres (genre_id, movie_id)
            VALUES (%s, %s)
            ON CONFLICT (genre_id, movie_id) DO NOTHING
            """,
            (genre_id, movie_id)
        )

    conn.commit()
    print("finish moviegenres")

    # ---------- ASSIGN ACTORS TO MOVIES ----------
    for actor_id, movie_id in STARS:
        cur.execute(
            """
            INSERT INTO movie_project.Stars (actor_id, movie_id)
            VALUES (%s, %s)
            ON CONFLICT (actor_id, movie_id) DO NOTHING
            """,
            (actor_id, movie_id)
        )

    conn.commit()
    print("finish stars")

    # ---------- INSERT REVIEWS ----------
    for review_id, user_name, movie_id, tc_str, rating, review_text in REVIEWS:
        tc = datetime.strptime(tc_str, '%Y-%m-%d')  if (tc_str) else None

        cur.execute(
            """
            INSERT INTO movie_project.Reviews (review_id, user_name, movie_id, time_created, rating, review_text)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (review_id) DO UPDATE
                SET user_name = EXCLUDED.user_name,
                    movie_id = EXCLUDED.movie_id,
                    time_created = EXCLUDED.time_created,
                    rating = EXCLUDED.rating,
                    review_text = EXCLUDED.review_text
            """,
            (review_id, user_name, movie_id, tc, rating, review_text)
        )

    conn.commit()
    print("finish reviews")
except Exception as e:
        conn.rollback()
        print("❌ Error:", e)
finally:
    cur.close()
    conn.close()