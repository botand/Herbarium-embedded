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
        :rtype: StatusIndicatorService
        """
        if DatabaseService.__instance is None:
            DatabaseService.__instance = DatabaseService()
        return DatabaseService.__instance

    def __init__(self):
        self._db = sqlite.connect(_db_path)

    def execute(self, sql, parameters=None):
        """
        Execute a SQL request.
        :param sql:
        :type sql: str
        :param parameters:
        :type parameters Iterable
        :return:
        """

        if parameters is None:
            parameters = []
        self._db.execute(sql, parameters)
