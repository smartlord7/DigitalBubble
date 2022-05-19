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

import jwt
import flask
import logging
from hashlib import sha512
from functools import wraps
from flask import request, jsonify
from hashlib import sha512
from http import HTTPStatus

import psycopg2

from data.enum.role_enum import Roles
from db.util import get_connection


app = flask.Flask(__name__)
app.config['SECRET_KEY'] = '004f2af45d3a4e161a7dd2d17fdae47f'
app.config['API_PREFIX'] = 'digitalbubble'
logger = None


def authorization(f=None, role=None):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not request:
            return None
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
@app.route(f'/{app.config["API_PREFIX"]}')
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
@app.route(f'/{app.config["API_PREFIX"]}/user/', methods=['POST'])
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

    if 'username' and 'email' and 'password' and 'first_name' and 'last_name' and 'tin' and 'phone_number' \
            and 'house_no' and 'street_name' and 'city' and 'state' and 'zip_code' and 'role' not in payload:
        response = {'status': HTTPStatus.BAD_REQUEST,
                    'results': 'invalid input in payload'}
        return flask.jsonify(response)

    password_hash = sha512(payload['password'].encode()).hexdigest()

    statement_user = 'INSERT INTO user (username, first_name, email, tin, last_name, phone_number, password_hash, \
        house_no, street_name, city, state, zip_code) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) returning id'
    values_user = (payload['username'], payload['first_name'], payload['email'], payload['tin'], payload['last_name'], payload['phone_number'],
                   password_hash, payload['house_no'], payload['street_name'], payload['city'], payload['state'], payload['zid_code'])

    try:
        cur.execute(statement_user, values_user)
        insert_id = cur.fetchone()

        if (payload['role'] == Roles['Admin']):
            statement = 'INSERT INTO admin (user_id) VALUES (%s)'
            values = (insert_id)
        elif (payload['role'] == Roles['Seller']):
            if 'company_name' not in payload:
                response = {'status': HTTPStatus.BAD_REQUEST,
                            'results': 'invalid input in payload'}
                return flask.jsonify(response)
            statement = 'INSERT INTO seller (user_id, company_name) VALUES (%s, %s)'
            values = (insert_id, payload['company_name'])
        elif (payload['role'] == Roles['Buyer']):
            statement = f'INSERT INTO buyer (user_id) VALUES (%s)'
            values = (insert_id)
        else:
            response = {'status': HTTPStatus.BAD_REQUEST,
                        'results': 'invalid input in payload'}
            return flask.jsonify(response)

        cur.execute(statement, values)

        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST {app.config["API_PREFIX"]}/user/ - error: {error}')
        response = {'status': HTTPStatus.INTERNAL_SERVER_ERROR,
                    'error': str(error)}

        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


# User authentication
@app.route(f'/{app.config["API_PREFIX"]}/user/', methods=['PUT'])
def login():
    """Function that a user login with his username and password

    Returns:
        _type_: _description_
    """

    logger.info('PUT /user')
    conn = get_connection()
    cur = conn.cursor()
    payload = flask.request.get_json()

    user_name = payload['user_name']

    cur.execute('SELECT password_hash '
                'FROM "user"'
                'WHERE user_name = %s', (user_name,))

    rows = cur.fetchall()

    if len(rows) == 0:
        error = f'User {user_name} not found'
        logger.error(f'PUT /user/ - error: {error}')
        response = {'status': HTTPStatus.BAD_REQUEST, 'errors': str(error)}
    else:
        user = rows[0]
        password = payload['password']
        password_hash = sha512(password.encode()).hexdigest()
        password_hash2 = user[0]

        if password_hash != password_hash2:
            error = f'Wrong password'
            logger.error(f'PUT /user/ - error: {error}')
            response = {'status': HTTPStatus.BAD_REQUEST, 'errors': str(error)}
        else:
            token = jwt.encode(
                payload=payload,
                key=app.config['SECRET_KEY'],
                algorithm='HS256',
            )

            response = {
                'status': HTTPStatus.OK,
                'results': token
            }

    return flask.jsonify(response)


# Create new product
@app.route(f'/{app.config["API_PREFIX"]}/product/', methods=['POST'])
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
        response = {'status': HTTPStatus.BAD_REQUEST,
                    'results': 'invalid input in payload'}
        return flask.jsonify(response)


# Update a product
@app.route(f'/{app.config["API_PREFIX"]}/product/<product_id>', methods=['PUT'])
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
        response = {'status': HTTPStatus.BAD_REQUEST,
                    'results': 'invalid input in payload'}
        return flask.jsonify(response)


# Buy a product
@app.route(f'/{app.config["API_PREFIX"]}/order/', methods=['POST'])
def buy_product():
    logger.info('POST /order')
    payload = flask.request.get_json()

    conn = get_connection()
    cur = conn.cursor()

    logger.debug(f'POST /order - payload: {payload}')

    if 'username' and 'email' and 'password' not in payload:
        response = {'status': HTTPStatus.BAD_REQUEST,
                    'results': 'invalid input in payload'}
        return flask.jsonify(response)


# Rate a product
@app.route(f'/{app.config["API_PREFIX"]}/rating/<product_id>', methods=['POST'])
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
        response = {'status': HTTPStatus.BAD_REQUEST,
                    'results': 'invalid input in payload'}
        return flask.jsonify(response)


# Create a comment
@app.route(f'/{app.config["API_PREFIX"]}/questions/<product_id>', methods=['POST'])
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
        response = {'status': HTTPStatus.BAD_REQUEST,
                    'results': 'invalid input in payload'}
        return flask.jsonify(response)


# Rply a comment
@app.route(f'/{app.config["API_PREFIX"]}/questions/<product_id>/<parent_question_id>', methods=['POST'])
def reply_comment(product_id, parent_question_id):
    """Function that replies to a comment.

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
        response = {'status': HTTPStatus.BAD_REQUEST,
                    'results': 'invalid input in payload'}
        return flask.jsonify(response)


# Get information of a product
@app.route(f'/{app.config["API_PREFIX"]}/product/<product_id>', methods=['GET'])
def get_product(product_id):
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
        response = {'status': HTTPStatus.BAD_REQUEST,
                    'results': 'invalid input in payload'}
        return flask.jsonify(response)


# Get statistics of the last 12 months
@app.route(f'/{app.config["API_PREFIX"]}/report/year', methods=['GET'])
def get_product_stats():
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
        response = {'status': HTTPStatus.BAD_REQUEST,
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
    logger.info(f'API v1 online: http://{host}:{port}//{app.config["API_PREFIX"]}')
    app.run(host=host, debug=True, threaded=True, port=port)
