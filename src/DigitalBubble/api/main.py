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

import jwt
import flask
import logging
from functools import wraps
from flask import request, jsonify

from db.util import get_connection

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = '004f2af45d3a4e161a7dd2d17fdae47f'
app.config['API_PREFIX'] = 'digitalbubble'

StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}


def authorization(f=None, role=None):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'})
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = None
        except:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)

    return decorator


##########################################################
## DATABASE ACCESS
##########################################################


@authorization(role="Admin")
@app.route(f'{app.config["API_PREFIX"]}/')
def landing_page():
    return """

    Hello World (Python API)!  <br/>
    <br/>
    Check the sources for instructions on how to use the endpoints!<br/>
    <br/>
    Digital Bubble<br/>
    <br/>
    """

@app.route(f'{app.config["API_PREFIX"]}/user/', methods=['POST'])
def register():
    logger.info('POST /user')
    payload = flask.request.get_json()

    conn = get_connection()
    cur = conn.cursor()

    logger.debug(f'POST /user - payload: {payload}')

    if 'username' and 'email' and 'password' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'invalid input in payload'}
        return flask.jsonify(response)


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
