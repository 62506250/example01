import os
import sqlite3
import hashlib
import secrets


class DataManager:

    def __init__(self, database_file):
        self._database_file = database_file
        self._ensure_database()

    def _open_connection(self):
        connection = sqlite3.connect(self._database_file)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _ensure_database(self):
        directory = os.path.dirname(self._database_file)
        if directory:
            os.makedirs(directory, exist_ok=True)

        connection = self._open_connection()
        try:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    salt TEXT NOT NULL,
                    password_hash TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS leaderboard (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.commit()
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
            connection.execute(
                "INSERT INTO users (username, salt, password_hash) VALUES (?, ?, ?)",
                (username, salt, password_hash),
            )
            connection.commit()
        except sqlite3.IntegrityError:
            return False, "That username is already taken."
        finally:
            connection.close()

        return True, "Account created! You can log in now."

    def login(self, username, password):
        username = username.strip()

        connection = self._open_connection()
        try:
            row = connection.execute(
                "SELECT salt, password_hash FROM users WHERE username = ?",
                (username,),
            ).fetchone()
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
            rows = connection.execute(
                "SELECT username, score FROM leaderboard "
                "ORDER BY score DESC, id ASC LIMIT 100"
            ).fetchall()
        finally:
            connection.close()

        leaderboard = []
        for row in rows:
            leaderboard.append({"username": row["username"], "score": row["score"]})
        return leaderboard

    def add_score(self, username, score):
        connection = self._open_connection()
        try:
            connection.execute(
                "INSERT INTO leaderboard (username, score) VALUES (?, ?)",
                (username, score),
            )
            connection.commit()
        finally:
            connection.close()
