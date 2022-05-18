##
# =============================================
# ============== Bases de Dados ===============
# ============== LEI  2021/2022 ===============
# =============================================
# === Department of Informatics Engineering ===
# =========== University of Coimbra ===========
# =============================================
##
# Authors:
# André Colaço       <andrecolaco@student.dei.uc.pt>
# Sancho Simoes      <sanchosimoes@student.dei.uc.pt>
# Rodrigo Machado    <ramachado@student.dei.uc.pt>

from multiprocessing import parent_process
import jwt
import flask
import logging
from functools import wraps
from flask import request, jsonify

from data.enum.status_code_enum import StatusCodes
from db.util import get_connection

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = '004f2af45d3a4e161a7dd2d17fdae47f'
app.config['API_PREFIX'] = 'digitalbubble'


def authorization(f=None, role=None):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'})
        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = None
        except:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)

    return decorator


##########################################################
# DATABASE ACCESS
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


# User registration
@app.route(f'{app.config["API_PREFIX"]}/user/', methods=['POST'])
def register():
    """Function that register new users

    Returns:
        _type_: _description_
    """

    logger.info('POST /user')
    payload = flask.request.get_json()

    conn = get_connection()
    cur = conn.cursor()

    logger.debug(f'POST /user - payload: {payload}')

    if 'username' and 'email' and 'password' not in payload:
        response = {'status': StatusCodes['api_error'],
                    'results': 'invalid input in payload'}
        return flask.jsonify(response)


# User autentication
@app.route(f'{app.config["API_PREFIX"]}/user/', methods=['PUT'])
def login():
    """Function that a user login with his username and password

    Returns:
        _type_: _description_
    """

    logger.info('PUT /user')
    payload = flask.request.get_json()

    conn = get_connection()
    cur = conn.cursor()

    logger.debug(f'PUT /user - payload: {payload}')

    if 'username' and 'email' and 'password' not in payload:
        response = {'status': StatusCodes['api_error'],
                    'results': 'invalid input in payload'}
        return flask.jsonify(response)


# Create new product
@app.route(f'{app.config["API_PREFIX"]}/product/', methods=['POST'])
def create_product():
    """Function that creates a new product

    Returns:
        _type_: _description_
    """

    logger.info('POST /product')
    payload = flask.request.get_json()

    conn = get_connection()
    cur = conn.cursor()

    logger.debug(f'POST /product - payload: {payload}')

    if 'username' and 'email' and 'password' not in payload:
        response = {'status': StatusCodes['api_error'],
                    'results': 'invalid input in payload'}
        return flask.jsonify(response)


# Update a product
@app.route(f'{app.config["API_PREFIX"]}/product/<product_id>', methods=['PUT'])
def update_product(product_id):
    """Function that updates an existing product

    Args:
        product_id (int): id of the product you want to update

    Returns:
        _type_: _description_
    """

    logger.info('PUT /product/<product_id>')

    logger.debug(f'product_id: {product_id}')

    payload = flask.request.get_json()

    conn = get_connection()
    cur = conn.cursor()

    logger.debug(f'PUT /product/<product_id> - payload: {payload}')

    if 'username' and 'email' and 'password' not in payload:
        response = {'status': StatusCodes['api_error'],
                    'results': 'invalid input in payload'}
        return flask.jsonify(response)


# Buy a product
@app.route(f'{app.config["API_PREFIX"]}/order/', methods=['POST'])
def buy_product():
    logger.info('POST /order')
    payload = flask.request.get_json()

    conn = get_connection()
    cur = conn.cursor()

    logger.debug(f'POST /order - payload: {payload}')

    if 'username' and 'email' and 'password' not in payload:
        response = {'status': StatusCodes['api_error'],
                    'results': 'invalid input in payload'}
        return flask.jsonify(response)


# Rate a product
@app.route(f'{app.config["API_PREFIX"]}/rating/<product_id>', methods=['POST'])
def rate_product(product_id):
    """Function that rates a product with a rating(0-5) and a comment.

    Args:
        product_id (int): id of the product you want to rate

    Returns:
        _type_: _description_
    """

    logger.info('POST /rating/<product_id>')

    logger.debug(f'product_id: {product_id}')

    payload = flask.request.get_json()

    conn = get_connection()
    cur = conn.cursor()

    logger.debug(f'POST /rantiing/<product_id> - payload: {payload}')

    if 'username' and 'email' and 'password' not in payload:
        response = {'status': StatusCodes['api_error'],
                    'results': 'invalid input in payload'}
        return flask.jsonify(response)


# Create a comment
@app.route(f'{app.config["API_PREFIX"]}/questions/<product_id>', methods=['POST'])
def create_comment(product_id):
    """Function that creates a comment.

    Args:
        product_id (int): id of the product you want to comment

    Returns:
        _type_: _description_
    """

    logger.info('POST /questions/<product_id>')

    logger.debug(f'product_id: {product_id}')

    payload = flask.request.get_json()

    conn = get_connection()
    cur = conn.cursor()

    logger.debug(f'POST /questions/<product_id> - payload: {payload}')

    if 'username' and 'email' and 'password' not in payload:
        response = {'status': StatusCodes['api_error'],
                    'results': 'invalid input in payload'}
        return flask.jsonify(response)


# Rply a comment
@app.route(f'{app.config["API_PREFIX"]}/questions/<product_id>/<parent_question_id>', methods=['POST'])
def reply_comment(product_id, parent_question_id):
    """Function that replies a comment.

    Args:
        product_id (int): id of the product you want to reply

    Returns:
        _type_: _description_
    """

    logger.info('POST /questions/<product_id>/<parent_question_id>')

    logger.debug(
        f'product_id: {product_id}, parent_question_id: {parent_question_id}')

    payload = flask.request.get_json()

    conn = get_connection()
    cur = conn.cursor()

    logger.debug(
        f'POST /questions/<product_id>/<parent_question_id> - payload: {payload}')

    if 'username' and 'email' and 'password' not in payload:
        response = {'status': StatusCodes['api_error'],
                    'results': 'invalid input in payload'}
        return flask.jsonify(response)


# Get information of a product
@app.route(f'{app.config["API_PREFIX"]}/product/<product_id>', methods=['GET'])
def get_product_information(product_id):
    """Function that gets the information of a product.

    Args:
        product_id (int): id of the product you want to get the information

    Returns:
        _type_: _description_
    """

    logger.info('GET /product/<product_id>')

    logger.debug(f'product_id: {product_id}')

    payload = flask.request.get_json()

    conn = get_connection()
    cur = conn.cursor()

    logger.debug(f'GET /product/<product_id> - payload: {payload}')

    if 'username' and 'email' and 'password' not in payload:
        response = {'status': StatusCodes['api_error'],
                    'results': 'invalid input in payload'}
        return flask.jsonify(response)


# Get statistics of the last 12 months
@app.route(f'{app.config["API_PREFIX"]}/report/year', methods=['GET'])
def get_product_statistics():
    """Function that gets the statistics of a product.

    Args:
        product_id (int): id of the product you want to get the statistics

    Returns:
        _type_: _description_
    """

    logger.info('GET /report/year')

    payload = flask.request.get_json()

    conn = get_connection()
    cur = conn.cursor()

    logger.debug(f'GET /report/year - payload: {payload}')

    if 'username' and 'email' and 'password' not in payload:
        response = {'status': StatusCodes['api_error'],
                    'results': 'invalid input in payload'}
        return flask.jsonify(response)


if __name__ == "__main__":
    # set up logging
    logging.basicConfig(filename='log_file.log')
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    host = '127.0.0.1'
    port = 8080
    app.run(host=host, debug=True, threaded=True, port=port)
    logger.info(f'API v1 online: http://{host}:{port}')
