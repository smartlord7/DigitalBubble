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
from typing import Union, Tuple, Any

import jwt
import flask
import logging
from functools import wraps
from flask import request, jsonify
from hashlib import sha512
from http import HTTPStatus
import psycopg2
from data.enum.role_enum import Roles
from data.model.seller import Seller
from data.model.user import User
from db.util import get_connection

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = '004f2af45d3a4e161a7dd2d17fdae47f'
app.config['API_PREFIX'] = 'digitalbubble'
logger = None


def authorization(f=None, roles=None):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not request:
            return None
        token = None
        if "HTTP_AUTHORIZATION" in request.environ:
            token = request.environ["HTTP_AUTHORIZATION"]

        if not token:
            return jsonify({'message': 'a valid token is missing'}), HTTPStatus.UNAUTHORIZED
        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=["HS256"])
            if roles != 'all' and data['role'] not in roles:
                return jsonify({}), HTTPStatus.UNAUTHORIZED
        except:
            return jsonify({'message': 'token is invalid'}), HTTPStatus.UNAUTHORIZED

        return f(data, *args, **kwargs)

    return decorator


def get_jwt_data():
    token = None

    if "HTTP_AUTHORIZATION" in request.environ:
        token = request.environ["HTTP_AUTHORIZATION"]

    if not token:
        return None
    try:
        token = token.replace("Bearer ", "")
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])

        return data
    except:
        return None

##########################################################
# DATABASE ACCESS
##########################################################


@authorization(roles="Admin")
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
    status = HTTPStatus.OK
    response = dict()

    logger.debug(f'POST /user - payload: {payload}')

    if payload['role'] == Roles['Admin'] or payload['role'] == Roles['Seller']:
        jwt_data = get_jwt_data()

        if not jwt_data:
            return jsonify({'error': 'Invalid token'}), HTTPStatus.UNAUTHORIZED

        if jwt_data["role"] != Roles["Admin"]:
            return jsonify({}), HTTPStatus.UNAUTHORIZED

    if payload['role'] == Roles['Seller']:
        u = Seller()
    else:
        u = User()
    error_response = u.bind_json(payload)
    if error_response:
        return error_response, HTTPStatus.BAD_REQUEST

    password_hash = sha512(payload['password'].encode()).hexdigest()
    conn = get_connection()
    cur = conn.cursor()
    statement_user = 'INSERT INTO "user" (user_name, first_name, email, tin, role, last_name, phone_number, password_hash, \
        house_no, street_name, city, state, zip_code) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) returning id'
    values_user = (u.user_name, u.first_name, u.email, u.tin, u.role, u.last_name,
                   u.phone_number, password_hash, u.house_no, u.street_name,
                   u.city, u.state, u.zip_code)

    try:
        cur.execute(statement_user, values_user)
        insert_id = cur.fetchone()
        if payload['role'] == Roles['Admin']:
            statement = 'INSERT INTO admin (user_id) VALUES (%s)'
            values = insert_id
        elif payload['role'] == Roles['Seller']:
            statement = 'INSERT INTO seller (user_id, company_name) VALUES (%s, %s)'
            values = (insert_id, u.company_name)
        else:
            statement = f'INSERT INTO buyer (user_id) VALUES (%s)'
            values = insert_id

        response['result'] = insert_id

        cur.execute(statement, values)
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST {app.config["API_PREFIX"]}/user/ - error: {error}')
        response = {'error': str(error)}
        status = HTTPStatus.INTERNAL_SERVER_ERROR

        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response), status


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

    cur.execute('SELECT id, role, password_hash '
                'FROM "user"'
                'WHERE user_name = %s', (user_name,))

    rows = cur.fetchall()

    if len(rows) == 0:
        error = f'User {user_name} not found'
        logger.error(f'PUT /user/ - error: {error}')

        return flask.jsonify({'error': str(error)}), HTTPStatus.BAD_REQUEST
    else:
        user = rows[0]
        password = payload['password']
        password_hash = sha512(password.encode()).hexdigest()
        role = user[0]
        password_hash2 = user[1]

        if password_hash != password_hash2:
            error = f'Wrong password'
            logger.error(f'PUT /user/ - error: {error}')
            response = {'error': str(error)}

            return flask.jsonify(response), HTTPStatus.BAD_REQUEST
        else:
            token = jwt.encode(
                payload={
                    "id": id,
                    "user_name": user_name,
                    "role": role
                },
                key=app.config['SECRET_KEY'],
                algorithm='HS256',
            )

            response = {
                'result': token
            }

    return flask.jsonify(response), HTTPStatus.OK


@authorization(roles=[Roles["Seller"]])
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


@authorization(roles=[Roles["Seller"]])
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

    cur = get_connection().cursor()

    logger.debug(f'PUT /product/<product_id> - payload: {payload}')

    if 'username' and 'email' and 'password' not in payload:
        response = {'status': HTTPStatus.BAD_REQUEST,
                    'results': 'invalid input in payload'}
        return flask.jsonify(response)


@authorization(roles=[Roles["Buyer"]])
@app.route(f'/{app.config["API_PREFIX"]}/order/', methods=['POST'])
def place_order():
    logger.info('POST /order')
    payload = flask.request.get_json()

    conn = get_connection()
    cur = conn.cursor()
    logger.debug(f'POST /order - payload: {payload}')

    cart = payload['cart']
    item_list = list()
    for item in cart:
        product_id = item[0]
        product_quantity = item[1]






    return flask.jsonify({})


@authorization(roles=[Roles["Buyer"]])
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


@authorization(roles="all")
@app.route(f'/{app.config["API_PREFIX"]}/questions/<product_id>/<parent_comment_id>', methods=['POST'])
def create_comment(product_id, parent_comment_id):
    """Function that creates a comment.

    Args:
        product_id (int): id of the product you want to comment

    Returns:
        _type_: _description_
    """

    logger.info('POST /questions/<product_id>')

    logger.debug(f'product_id: {product_id}, parent_comment_id: {parent_comment_id}')

    payload = flask.request.get_json()

    conn = get_connection()
    cur = conn.cursor()

    logger.debug(f'POST /questions/<product_id> - payload: {payload}')

    if 'username' and 'email' and 'password' not in payload:
        response = {'status': HTTPStatus.BAD_REQUEST,
                    'results': 'invalid input in payload'}
        return flask.jsonify(response)


@authorization(roles="all")
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

    return flask.jsonify({})


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

    return flask.jsonify({})


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
