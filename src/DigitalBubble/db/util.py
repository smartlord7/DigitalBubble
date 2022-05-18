import psycopg2


def get_connection():
    conn = psycopg2.connect(
        user='',
        password='',
        host='127.0.0.1',
        port='5432',
        database=''
    )

    return conn
