# 🎬 Movie Project – Full Stack Application

This project is a simple full-stack movie web application built using Python, Flask, PostgreSQL, HTML, and CSS.

The application allows users to:
- View randomly selected movies on the home page
- View detailed movie pages (cast, genres, reviews)
- View actor detail pages
- Search for movies by title
- Add reviews for movies

---

## 📁 Project Structure

```text
movie_project/
│
├── app.py
├── db.py
├── movies.sql
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── movie.html
│   ├── actor.html
│
├── static/
│   ├── style.css
│   └── script.js
│
└── venv/
```

## 1. Prerequisites

Before running this project, make sure the following software is installed on your local machine:

- **Python 3.9 or newer**
- **PostgreSQL**
- **DBeaver** (recommended for database management)

Verify that Python and PostgreSQL are installed by running:

```bash
python3 --version
psql --version
```

## 2. Clone the Repository

Clone this repository to your local machine and navigate into the project directory:

```bash
git clone <your-repository-url>
cd <your-project-folder>
```

## 3. Create and Activate a Virtual Environment

Create a Python virtual environment to manage dependencies:
```bash
python3 -m venv venv
```

Activate the virtual environment:

**macOS / Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

## 4. Install Required Python Packages

With the virtual environment activated, install the required dependencies:
```bash
python3 -m pip install psycopg2-binary requests flask
```

## 5. Set Up the PostgreSQL Database

### 5.1 Create the Database

Open PostgreSQL (via `psql` or DBeaver) and create a new database:
```sql
CREATE DATABASE movies;
```

### 5.2 Import the Database Dump

This project includes a PostgreSQL dump file named `movies.sql`.

1. Open DBeaver
2. Connect to your PostgreSQL server
3. Select the `movies` database
4. Open the SQL Editor
5. Import and run the `movies.sql` file

### 5.3 Verify Schema Name

After importing, make sure the schema name is:
```
movie_project
```

If needed, set it as the default schema in your SQL client.

## 6. Configure Database Connection

In the backend Python file (e.g. `app.py`), ensure the database connection matches your local setup:
```python
conn = psycopg2.connect(
    dbname="movies",
    user="your_postgres_username",
    password="your_postgres_password",
    host="localhost",
    port="5432"
)
```

Replace:
- `your_postgres_username`
- `your_postgres_password`

with your actual PostgreSQL credentials.

## 7. Run the Backend Server

Start the Flask backend server on port 8000:
```bash
python app.py
```

You should see output similar to:
```
Running on http://127.0.0.1:8000/
```

## 8. Open the Application in Browser

Open your browser and navigate to:
```
http://localhost:8000
```

## 9. Application Features

The application supports the following features:

- View 20 random movies on the home page
- Click a movie to view:
  - Movie details
  - Cast (with images)
  - User reviews
- Horizontally scrollable cast section
- Click an actor to view actor details
- Search movies by title
- Add a review using a chosen `user_name`

## 10. Stopping the Server

To stop the server, press `CTRL + C` in the terminal where the Flask app is running.