import os
import sqlite3 as sqlite


class GreenhouseDatabase(object):
    def __init__(self, db_path="/home/pi/.greenhouse/greenhouse.db"):
        """
        Connect to SQLite database.
        db_path defaults to /home/pi/.greenhouse/greenhouse.db
        """
        path = "/".join(db_path.split("/")[:-1])
        filename = db_path.split("/")[:-1]

        if not os.path.exists(path):
            os.makedirs(path)

        self.db = sqlite.connect(db_path)
        self.cursor = self.db.cursor()

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS
                greenhouse (
                    datetime TEXT,
                    pot_number REAL,
                    humidity REAL,
                    tank_level REAL,
                    soil REAL,
                    light REAL
                )
        """
        )
        self.db.commit()

    def record_sensor_values(self, values):
        """
        Save sensor readings to database
        """
        self.cursor.execute(
            """
            INSERT INTO
                greenhouse
            VALUES
                (?, ?, ?, ?, ?,?)
        """,
            values,
        )
        self.db.commit()

    def get_sensor_value(self, sensor):
        """
        Look up the latest single sensor value from the database
        e.g. get_sensor_value('humidity')
        """
        self.cursor.execute(
            """
            SELECT
                *
            FROM
                greenhouse
            ORDER BY
                datetime(datetime) DESC
            LIMIT
                0, 1
        """
        )
        result = self.cursor.fetchone()
        if not result:
            return None

        datetime, pot_number, humidity, tank_level, light = result
        sensor_values = {
            "pot_number": pot_number,
            "humidity": humidity,
            "tank_level": tank_level,
            "soil": soil,
            "light": light,
        }
        return sensor_values[sensor]

    def export_to_csv(self, file_path=None):
        """
        Export sensor data from database and save as CSV file in file_path
        file_path defaults to /home/pi/greenhouse.csv
        """
        if file_path is None:
            file_path = "/home/pi/greenhouse.csv"

        self.cursor.execute(
            """
            SELECT
                *
            FROM
                greenhouse
        """
        )

        results = self.cursor.fetchall()

        with open(file_path, "w") as f:
            f.write("Date/Time,pot_number,Humidity,tank_level,soil,Light\n")
            for result in results:
                for data in result:
                    f.write("%s," % data)
                f.write("\n")


def main():
    db = GreenhouseDatabase()
    print(db.get_sensor_value("pot_number"))
    db.export_to_csv()


if __name__ == "__main__":
    main()
