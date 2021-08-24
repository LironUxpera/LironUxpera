import psycopg2
import json


class SendCommand:
    def __init__(self):
        self.username = 'uxpera'  # 'harry@nommerus.com'
        self.password = 'mzAuznh6v0DtwXeajyQc'  # '!9tEQ3$rrZ6qer'
        self.host = 'main.czeaa3vdlzib.us-east-1.rds.amazonaws.com'
        self.port = 5432
        self.connection = None

        self.connect()

    def connect(self):
        self.connection = psycopg2.connect(user=self.username, password=self.password, host=self.host,
                                           port=self.port, database="uxpera")

    def print_server_info(self):
        cursor = self.connection.cursor()

        # Print PostgreSQL details
        print("PostgreSQL server information")
        print(self.connection.get_dsn_parameters(), "\n")

        # Executing a SQL query
        cursor.execute("SELECT version();")
        # Fetch result
        record = cursor.fetchone()
        print("You are connected to - ", record, "\n")

    def fetch_responder_records(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * from responder")
        result = cursor.fetchall()
        return result

    def push_banner_to_user(self, client, uuid, banner_html):
        cursor = self.connection.cursor()

        # Create a new record
        sql = "INSERT INTO responder (client_id, user_uuid, response_type, html, configuration) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (client, uuid, 'banner', banner_html, json.dumps({})))

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        self.connection.commit()
