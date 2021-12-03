"""Service to interact with the database"""
import os
import sqlite3 as sqlite
import threading

from src.utils.logger import get_logger

_SERVICE_TAG = "services.DatabaseService"
_db_path = os.getenv("DB_FILE", ".database.db")
_db_init_scripts_dir = os.path.join(
    os.path.dirname(__file__), "../../database/upgrades"
)

lock = threading.Lock()


class DatabaseService:
    """Service to interact with the database"""

    __instance = None

    _logger = get_logger(_SERVICE_TAG)

    @staticmethod
    def instance():
        """
        Get the service
        :rtype: DatabaseService
        """
        if DatabaseService.__instance is None:
            DatabaseService.__instance = DatabaseService()
        return DatabaseService.__instance

    def __init__(self):
        """Initialize the service"""
        self._db = sqlite.connect(_db_path, timeout=10, check_same_thread=False)

        self._logger.info("initialized")

    def execute(self, query, parameters=None, commit=True):
        """
        Execute a SQL request. This function doesn't return the result of the query
        :param query: SQL query to execute.
        :type query: str
        :param parameters: all the parameters for the query.
        :type parameters Iterable|dict
        :param commit: do we need to commit the cursor
        :type commit: bool
        :return the results of the query
        :rtype: list
        """
        lock.acquire(blocking=True)
        self._logger.debug(
            "Executing query: '%s' with params %s.", query, str(parameters)
        )
        cursor = self._db.execute(query)
        result = cursor.fetchall()
        if commit:
            self._db.commit()
        lock.release()
        self._logger.debug("Query results: %s", str(result))
        return result

    def close(self):
        """Closing the database connection"""
        self._logger.debug("Closing database connection")
        self._db.close()
        self._logger.info("Database connection closed")

    def run_init_scripts(self):
        """Run all the scripts contained in the database/upgrades folder."""
        self._logger.debug("Run the initialization scripts")

        files = os.listdir(_db_init_scripts_dir)
        for file_path in files:
            with open(f"{_db_init_scripts_dir}/{file_path}", "r") as file:
                self._db.executescript(file.read())
                self._db.commit()
                self._logger.debug("executing %s file", file_path)
