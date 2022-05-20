import psycopg2


class ConnectionFactory:
    def __init__(self) -> None:
        self.user = None
        self.password = None
        self.host = None
        self.port = None
        self.database = None


    def get_connection(self):
        conn = psycopg2.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database
        )
    
        conn.set_session(autocommit=False)

        return conn
