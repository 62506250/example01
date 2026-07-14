import hashlib
import secrets

import psycopg2
import psycopg2.extras


class DataManager:

    def __init__(self, db_config):
        self._db_config = db_config
        self._ensure_database()

    def _open_connection(self):
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
        connection = self._open_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    salt TEXT NOT NULL,
                    password_hash TEXT NOT NULL
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

    @staticmethod
    def _hash_password(password, salt):
        combined = salt + password
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    def sign_up(self, username, password):
        username = username.strip()
        if not username or not password:
            return False, "Username and password cannot be empty."

        salt = secrets.token_hex(8)
        password_hash = self._hash_password(password, salt)

        connection = self._open_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO users (username, salt, password_hash) VALUES (%s, %s, %s)",
                (username, salt, password_hash),
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
                "SELECT salt, password_hash FROM users WHERE username = %s",
                (username,),
            )
            row = cursor.fetchone()
            cursor.close()
        finally:
            connection.close()

        if row is None:
            return False, "No account with that username."

        expected_hash = self._hash_password(password, row["salt"])
        if expected_hash != row["password_hash"]:
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