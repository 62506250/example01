import psycopg2
import psycopg2.extras


class DataManager:
    """Handles the PostgreSQL database for accounts and the leaderboard."""

    def __init__(self, db_config):
        self._db_config = db_config
        self._ensure_database()

    def _open_connection(self):
        """Opens a new connection to the database."""
        connection = psycopg2.connect(
            host=self._db_config["host"],
            port=self._db_config["port"],
            dbname=self._db_config["dbname"],
            user=self._db_config["user"],
            password=self._db_config["password"],
            cursor_factory=psycopg2.extras.RealDictCursor,
        )
        return connection

    def _ensure_database(self):
        """Creates the database tables if they do not already exist."""
        connection = self._open_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS leaderboard (
                    id SERIAL PRIMARY KEY,
                    username TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP::text
                )
                """
            )
            connection.commit()
            cursor.close()
        finally:
            connection.close()

    def sign_up(self, username, password):
        username = username.strip()
        if not username or not password:
            return False, "Username and password cannot be empty."

        connection = self._open_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password),
            )
            connection.commit()
            cursor.close()
        except psycopg2.IntegrityError:
            connection.rollback()
            return False, "That username is already taken."
        finally:
            connection.close()

        return True, "Account created! You can log in now."

    def login(self, username, password):
        username = username.strip()

        connection = self._open_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT password FROM users WHERE username = %s",
                (username,),
            )
            row = cursor.fetchone()
            cursor.close()
        finally:
            connection.close()

        if row is None:
            return False, "No account with that username."

        if password != row["password"]:
            return False, "Incorrect password."

        return True, "Logged in."

    def load_leaderboard(self):
        connection = self._open_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT username, score FROM leaderboard "
                "ORDER BY score DESC, id ASC LIMIT 100"
            )
            rows = cursor.fetchall()
            cursor.close()
        finally:
            connection.close()

        leaderboard = []
        for row in rows:
            leaderboard.append({"username": row["username"], "score": row["score"]})
        return leaderboard

    def add_score(self, username, score):
        connection = self._open_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO leaderboard (username, score) VALUES (%s, %s)",
                (username, score),
            )
            connection.commit()
            cursor.close()
        finally:
            connection.close()