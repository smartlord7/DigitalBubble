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

import jwt
import flask
import logging
from functools import wraps
from flask import request, jsonify
from hashlib import sha512
from http import HTTPStatus
import psycopg2
from psycopg2 import extensions
from data.enum.role_enum import Roles
from data.enum.product_enum import Product_type
from data.model.classification import Classification
from data.model.comment import Comment
from data.model.seller import Seller
from data.model.user import User
from data.model.computer import Computer
from data.model.smartphone import Smartphone
from data.model.television import Television
from data.model.product import Product
from db.util import get_connection

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = '004f2af45d3a4e161a7dd2d17fdae47f'
app.config['API_PREFIX'] = 'digitalbubble'
logger = None


def authorization(roles):
    def authorization_(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            if not request:
                return None
            token = None
            if "HTTP_AUTHORIZATION" in request.environ:
                token = request.environ["HTTP_AUTHORIZATION"].replace("Bearer ", "")

            if not token:
                return jsonify({'error': 'a valid token is missing'}), HTTPStatus.UNAUTHORIZED
            try:
                data = jwt.decode(
                    token, app.config['SECRET_KEY'], algorithms=["HS256"])
                if roles != 'all' and data['role'] not in roles:
                    return jsonify({}), HTTPStatus.UNAUTHORIZED
            except:
                return jsonify({'error': 'token is invalid'}), HTTPStatus.UNAUTHORIZED

            return f(*args, **kwargs)

        return decorator

    return authorization_


def get_session():
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
        session = get_session()

        if not session:
            return jsonify({'error': 'Invalid token'}), HTTPStatus.UNAUTHORIZED

        if session["role"] != Roles["Admin"]:
            return jsonify({}), HTTPStatus.UNAUTHORIZED

    if payload['role'] == Roles['Seller']:
        u = Seller()
    else:
        u = User()
    model_errors = u.bind_json(payload)
    if model_errors:
        return model_errors, HTTPStatus.BAD_REQUEST

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
            statement = 'INSERT INTO buyer (user_id) VALUES (%s)'
            values = insert_id

        response['result'] = insert_id

        cur.execute(statement, values)
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST {app.config["API_PREFIX"]}/user/ - error: {error}')
        response['error'] = str(error)
        status = HTTPStatus.INTERNAL_SERVER_ERROR

        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response), status


@app.route(f'/{app.config["API_PREFIX"]}/user/', methods=['PUT'])
def login():
    """Function that a user login with his username and password

    Returns:
        _type_: _description_
    """

    logger.info('PUT /user')
    response = dict()
    payload = flask.request.get_json()

    user_name = payload['user_name']
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('SELECT id, role, password_hash '
                'FROM "user"'
                'WHERE user_name = %s', (user_name,))

    rows = cur.fetchall()

    if len(rows) == 0:
        error = f'User {user_name} not found'
        logger.error(f'PUT /user/ - error: {error}')

        return jsonify({'error': str(error)}), HTTPStatus.BAD_REQUEST
    else:
        user = rows[0]
        password = payload['password']
        password_hash = sha512(password.encode()).hexdigest()
        user_id = user[0]
        role = user[1]
        password_hash2 = user[2]

        if password_hash != password_hash2:
            error = f'Wrong password'
            logger.error(f'PUT /user/ - error: {error}')
            response['error'] = str(error)

            return jsonify(response), HTTPStatus.BAD_REQUEST
        else:
            token = jwt.encode(
                payload={
                    "id": user_id,
                    "user_name": user_name,
                    "role": role
                },
                key=app.config['SECRET_KEY'],
                algorithm='HS256',
            )

            response = {
                'result': token
            }

    return jsonify(response), HTTPStatus.OK


@app.route(f'/{app.config["API_PREFIX"]}/product/', methods=['POST'])
@authorization(roles=[Roles["Seller"]])
def create_product():
    """Function that creates a new product

    Returns:
        _type_: _description_
    """

    logger.info('POST /product')
    payload = flask.request.get_json()
    status = HTTPStatus.OK
    response = dict()

    conn = get_connection()
    cur = conn.cursor()

    logger.debug(f'POST /product - payload: {payload}')
    type_product = payload['type']

    if type_product == Product_type['Computer']:
        p = Computer()
    elif type_product == Product_type['Television']:
        p = Television()
    elif type_product == Product_type['Smartphone']:
        p = Smartphone()
    else:
        p = Product()

    model_errors = p.bind_json(payload)
    if model_errors:
        return model_errors, HTTPStatus.BAD_REQUEST

    session = get_session()
    seller_id = session['id']

    query_max_product_id = 'SELECT MAX(id) FROM product'
    cur.execute(query_max_product_id)
    max_product_id = cur.fetchone()[0]

    if not max_product_id:
        max_product_id = 1

    statement_product = 'INSERT INTO product (id, name, price, stock, description, category, seller_id, version) \
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s) returning id'
    values_product = (max_product_id, p.name, p.price, p.stock, p.description, p.category, seller_id, 1)

    try:
        cur.execute(statement_product, values_product)
        insert_id = cur.fetchone()
        type_product = payload['type']

        if type_product == Product_type['Computer']:
            statement = 'INSERT INTO computer ' \
                        '(cpu, gpu, product_id, product_version) ' \
                        'VALUES (%s, %s, %s, %s)'
            values = (p.cpu, p.gpu, insert_id, 1)
        elif type_product == Roles['Smartphone']:
            statement = 'INSERT INTO smartphone ' \
                        '(model, operative_system, product_id, product_version) ' \
                        'VALUES (%s, %s, %s)'
            values = (p.model, p.operative_system, insert_id, 1)
        else:
            statement = 'INSERT INTO television ' \
                        '(size, technology, product_id, product_version) ' \
                        'VALUES (%s, %s, %s, %s)'
            values = (p.size, p.technology, insert_id, 1)

        response['result'] = insert_id

        cur.execute(statement, values)
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST {app.config["API_PREFIX"]}/user/ - error: {error}')
        response['error'] = str(error)
        status = HTTPStatus.INTERNAL_SERVER_ERROR

        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response), status


@app.route(f'/{app.config["API_PREFIX"]}/product/<product_id>', methods=['PUT'])
@authorization(roles=[Roles["Seller"]])
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
    response = dict()
    status = HTTPStatus.OK
    session = get_session()
    conn = get_connection()
    cur = conn.cursor()

    user_id = session['id']

    try:
        product_statement = 'SELECT id, version, seller_id ' \
                            'FROM product ' \
                            'WHERE id = %s AND version = (SELECT MAX(version)' \
                            '                             FROM product ' \
                            '                             WHERE id = %s )'
        values = (product_id, product_id)

        cur.execute(product_statement, values)
        product = cur.fetchone()
        product_id = product[0]
        if product_id is None:
            return jsonify({}), HTTPStatus.NOT_FOUND

        version = product[1]
        seller_id = product[2]

        if seller_id != user_id:
            return jsonify({}), HTTPStatus.UNAUTHORIZED

        type_product = payload['type']
        if type_product == Product_type['Computer']:
            p = Computer()
        elif type_product == Product_type['Television']:
            p = Television()
        elif type_product == Product_type['Smartphone']:
            p = Smartphone()
        else:
            p = Product()

        model_errors = p.bind_json(payload)
        if model_errors:
            return model_errors, HTTPStatus.BAD_REQUEST
        statement_product = 'INSERT INTO product ' \
                            '(id, name, price, stock, description, category, seller_id, version) ' \
                            'VALUES(%s, %s, %s, %s, %s, %s, %s, %s)'
        values_product = (product_id, p.name, p.price, p.stock, p.description, p.category, seller_id, version + 1)

        cur.execute(statement_product, values_product)
        type_product = payload['type']

        if type_product == Product_type['Computer']:
            statement = 'INSERT INTO computer ' \
                        '(cpu, gpu, product_id, product_version) ' \
                        'VALUES (%s, %s, %s, %s)'
            values = (p.cpu, p.gpu, product_id, version + 1)
        elif type_product == Roles['Smartphone']:
            statement = 'INSERT INTO smartphone ' \
                        '(model, operative_system, product_id, product_version) ' \
                        'VALUES (%s, %s, %s, %s)'
            values = (p.model, p.operative_system, product_id, version + 1)
        else:
            statement = 'INSERT INTO television ' \
                        '(size, technology, product_id, product_version) ' \
                        'VALUES (%s, %s, %s, %s)'
            values = (p.size, p.technology, product_id, version + 1)

        response['result'] = product_id

        cur.execute(statement, values)
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'PUT {app.config["API_PREFIX"]}/product/<product_id> - error: {error}')
        response['error'] = str(error)
        status = HTTPStatus.INTERNAL_SERVER_ERROR

        conn.rollback()
    finally:
        if conn is not None:
            conn.close()

    return jsonify(response), status


@app.route(f'/{app.config["API_PREFIX"]}/rating/<product_id>', methods=['POST'])
@authorization(roles=[Roles["Admin"], Roles["Buyer"]])
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
    response = dict()
    status = HTTPStatus.OK
    session = get_session()
    conn = get_connection()
    cur = conn.cursor()

    logger.debug(f'POST /rating/<product_id> - payload: {payload}')

    c = Classification()

    model_errors = c.bind_json(payload)
    if model_errors:
        return model_errors, HTTPStatus.BAD_REQUEST

    try:
        buyer_id = session['id']
        statement_product = 'SELECT name ' \
                            'FROM product ' \
                            'WHERE id = %s'
        values = (product_id,)

        cur.execute(statement_product, values)
        product = cur.fetchone()

        if product[0] is None:
            return jsonify({}), HTTPStatus.NOT_FOUND

        classification_statement = 'INSERT INTO classification ' \
                                   '(rating, comment, buyer_id, product_id) ' \
                                   'VALUES (%s, %s, %s, %s)'
        values = (c.rating, c.comment, buyer_id, product_id)

        cur.execute(classification_statement, values)
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'PUT {app.config["API_PREFIX"]}/product/<product_id> - error: {error}')
        response['error'] = str(error)
        status = HTTPStatus.INTERNAL_SERVER_ERROR

        conn.rollback()
    finally:
        if conn is not None:
            conn.close()

    return jsonify(response), status


@app.route(f'/{app.config["API_PREFIX"]}/order/', methods=['POST'])
@authorization(roles=[Roles["Admin"], Roles["Buyer"]])
def create_order():
    logger.info('POST /order')
    payload = flask.request.get_json()

    conn = get_connection()
    cur = conn.cursor()
    status = HTTPStatus.OK
    response = dict()
    session = get_session()
    buyer_id = session['id']
    logger.debug(f'POST /order - payload: {payload}')
    conn.set_isolation_level(extensions.ISOLATION_LEVEL_SERIALIZABLE)
    try:
        order_statement = 'INSERT INTO "order"' \
                          '(order_timestamp, buyer_id, is_complete)' \
                          'VALUES (CURRENT_TIMESTAMP, %s, %s) returning id'
        values = (buyer_id, '0')
        cur.execute(order_statement, values)
        order_id = cur.fetchone()
        response = {'order_id': order_id}

        cart = payload['cart']
        for item in cart:
            product_id = item[0]
            product_quantity = item[1]

            product_statement = 'SELECT stock ' \
                                'FROM product ' \
                                'WHERE id = %s'
            values = (product_id,)
            cur.execute(product_statement, values)
            stock = cur.fetchone()[0]

            if stock is None:
                status = HTTPStatus.NOT_FOUND

                return jsonify({}), status

            if stock < product_quantity:
                status = HTTPStatus.BAD_REQUEST

                return jsonify({
                    'error': 'Insufficient stock for product: have %d' % stock
                }), status

            product_statement = "UPDATE product " \
                                "SET stock = stock - %s " \
                                "WHERE id = %s"
            values = (product_quantity, product_id)
            cur.execute(product_statement, values)

            item_statement = 'INSERT INTO item' \
                             '(quantity, product_id, order_id)' \
                             'VALUES (%s, %s, %s)'

            values = (product_quantity, product_id, order_id)
            cur.execute(item_statement, values)

        order_statement = 'UPDATE "order"' \
                          'SET is_complete = %s' \
                          'WHERE id = %s'
        values = ('1', order_id)
        cur.execute(order_statement, values)
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST {app.config["API_PREFIX"]}/order/ - error: {error}')
        response['error'] = str(error)
        status = HTTPStatus.INTERNAL_SERVER_ERROR

        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response), status


@app.route(f'/{app.config["API_PREFIX"]}/questions/<product_id>/', methods=['POST'])
@app.route(f'/{app.config["API_PREFIX"]}/questions/<product_id>/<parent_comment_id>', methods=['POST'])
@authorization(roles="all")
def create_comment(product_id, parent_comment_id=None):
    """Function that creates a comment.

    Args:
        product_id (int): id of the product you want to comment

    Returns:
        _type_: _description_
    """

    logger.info('POST /questions/<product_id>')
    logger.debug(f'product_id: {product_id}, parent_comment_id: {parent_comment_id}')
    payload = flask.request.get_json()
    status = HTTPStatus.OK
    response = dict()

    logger.debug(f'POST /questions/<product_id> - payload: {payload}')

    c = Comment()
    model_errors = c.bind_json(payload)
    if model_errors:
        return model_errors, HTTPStatus.BAD_REQUEST

    conn = get_connection()
    cur = conn.cursor()
    session = get_session()
    user_id = session['id']

    try:

        product_statement = 'SELECT name ' \
                            'FROM product ' \
                            'WHERE id = %s'
        values = (product_id,)
        cur.execute(product_statement, values)
        name = cur.fetchone()[0]

        if name is None:
            status = HTTPStatus.NOT_FOUND

            return jsonify({}), status

        comment_statement = 'INSERT INTO comment ' \
                            '(text, parent_id, user_id, product_id)' \
                            'VALUES (%s, %s, %s, %s) returning id'
        values = (c.text, parent_comment_id, user_id, product_id)
        cur.execute(comment_statement, values)
        conn.commit()
        comment_id = cur.fetchone()

        response['result'] = comment_id

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST {app.config["API_PREFIX"]}/order/ - error: {error}')
        response['error'] = str(error)
        status = HTTPStatus.INTERNAL_SERVER_ERROR

        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response), status


@app.route(f'/{app.config["API_PREFIX"]}/product/<product_id>', methods=['GET'])
@authorization(roles="all")
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

    return jsonify({})


@app.route(f'/{app.config["API_PREFIX"]}/report/year', methods=['GET'])
@authorization(roles=Roles["Admin"])
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

    return jsonify({})


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
