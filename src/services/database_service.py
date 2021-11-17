"""Service to interact with the database"""
from src.utils.logger import get_logger
import sqlite3 as sqlite
import os

_SERVICE_TAG = "services.DatabaseService"
_db_path = os.getenv("DB_FILE", ".database.db")


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
        self._db = sqlite.connect(_db_path)
        self._logger.info("initialized")

    def execute(self, query, parameters=None):
        """
        Execute a SQL request. This function doesn't return the result of the query
        :param query: SQL query to execute.
        :type query: str
        :param parameters: all the parameters for the query.
        :type parameters Iterable|dict
        :return the results of the query
        :rtype list
        """
        if parameters is None:
            parameters = []
        self._logger.info("Executing query: %s with params %s.", query, str(parameters))
        cursor = self._db.execute(query, parameters)
        result = cursor.fetchall()
        self._db.commit()
        self._logger.debug("Query results: %s", str(result))
        return result

    def close(self):
        """Closing the database connection"""
        self._logger.debug("Closing database connection")
        self._db.close()
        self._logger.info("Database connection closed")
