##
## =============================================
## ============== Bases de Dados ===============
## ============== LEI  2021/2022 ===============
## =============================================
## === Department of Informatics Engineering ===
## =========== University of Coimbra ===========
## =============================================
##
## Authors:
##   André Colaço       <andrecolaco@student.dei.uc.pt>
##   Sancho Simoes      <sanchosimoes@student.dei.uc.pt>  
##   Rodrigo Machado    <ramachado@student.dei.uc.pt>


import flask
import logging
from pip import main
import psycopg2

app = flask.Flask(__name__)

StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}

##########################################################
## DATABASE ACCESS
##########################################################

def db_connection():
    db = psycopg2.connect(
        user='',
        password='',
        host='127.0.0.1',
        port='5432',
        database=''
    )

    return db


@app.route('/')
def landing_page():
    return """

    Hello World (Python API)!  <br/>
    <br/>
    Check the sources for instructions on how to use the endpoints!<br/>
    <br/>
    Projeto BD<br/>
    <br/>
    """


@app.route('/user/', methods=['POST'])
def add_user():
    logger.info('POST /user')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /user - payload: {payload}')

    if 'username' and 'email' and 'password' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'invalid input in payload'}
        return flask.jsonify(response)

    # statement = 'INSERT INTO buyer (ndep, nome, local) VALUES (%s, %s, %s)'
    # values = (payload['ndep'], payload['localidade'], payload['nome'])


if __name__ == "__main__":
    
    # set up logging
    logging.basicConfig(filename='log_file.log')
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    host = '127.0.0.1'
    port = 8080
    app.run(host=host, debug=True, threaded=True, port=port)
    logger.info(f'API v1 online: http://{host}:{port}')
