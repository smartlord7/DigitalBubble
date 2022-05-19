import psycopg2


def get_connection():
    conn = psycopg2.connect(
        user='digitalbubbleadmin',
        password='digitalbubble123#',
        host='127.0.0.1',
        port='5432',
        database='DigitalBubble',
    )
    conn.set_session(autocommit=False)

    return conn
